import base64
import json
import os

import boto3
import requests
from github import Github, GithubException

from release_prep import ReleasePreparation


def on_github_push(event, context, dryrun=False):
    message = _process_event(event)
    ref = message["ref"]
    if ref == "refs/heads/master" or ref == "refs/heads/develop":
        repo_name = message["repository"]["full_name"]
        pusher = message["pusher"]["name"]
        api_key = os.environ['API_KEY']
        repo = Github(api_key).get_repo(repo_name)
        branch = repo.get_branch(ref)
        notification_message = "Commit to " + ref + " detected on " + repo_name + " branch " + branch.name + " by " + pusher
        print(notification_message)
        _send_notification(notification_message, context, dryrun)
        server_path = 'json_schema'
        versions_file = repo.get_contents(server_path + "/versions.json", branch.name)
        version_numbers = base64.b64decode(versions_file.content)
        result = _process_directory(repo, branch.name, server_path, version_numbers, context, dryrun)
        result_str = "\n".join(result)
        result_message = ""
        if len(result) == 0:
            result_message = result_message + "No schema changes published"
        else:
            result_message = result_message + "New schema changes published:\n" + result_str
        print(result_message)
        _send_notification(result_message, context, dryrun)
    else:
        result = []
    response = {
        "statusCode": 200,
        "body": {
            "created": json.dumps(result)
        }
    }
    return response


def _process_event(event):
    message = json.loads(event["body"])
    return message


def _process_directory(repo, branch_name, server_path, version_numbers, context, dryrun=False):
    print("Processing " + server_path + " in " + branch_name + " branch of " + repo.name)
    created_list = []
    contents = repo.get_dir_contents(server_path, branch_name)
    for content in contents:
        if content.type == 'dir':
            created_list.extend(_process_directory(repo, branch_name, content.path, version_numbers, context, dryrun))
        else:
            try:
                path = content.path
                file_root, file_extension = os.path.splitext(path)
                if file_extension == '.json':
                    print("- processing: " + path)
                    file_content = repo.get_contents(path, branch_name)
                    data = base64.b64decode(file_content.content)
                    json_data = json.loads(data.decode('utf8'))
                    release_preparation = ReleasePreparation()
                    expanded_file_data = release_preparation.expandURLs(server_path, path, json_data, version_numbers,
                                                                        branch_name)
                    key = _get_schema_key(expanded_file_data)
                    if key is None:
                        print("- could not find key for: " + path)
                    else:
                        created = _upload(key, branch_name, data, context, dryrun)
                        if created:
                            created_list.append(key)
                else:
                    print("- skipping: " + path)
            except(GithubException, IOError) as e:
                print('Error processing %s: %s', content.path, e)
    return created_list


def _upload(key, branch_name, file_data, context, dryrun=False):
    if dryrun:
        return True
    else:
        if branch_name == "develop":
            bucket = os.environ['DEV_BUCKET']
        else:
            bucket = os.environ['PROD_BUCKET']
        s3 = boto3.client('s3')
        if not _key_exists(s3, bucket, key):
            try:
                s3.put_object(Bucket=bucket, Key=key, Body=file_data, ContentType='application/json', ACL='public-read')
                return True
            except Exception as e:
                error_message = 'Error uploading ' + key
                print(error_message, e)
                _send_notification(error_message, context, dryrun)
        else:
            return False


def _key_exists(s3, bucket, key):
    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )
    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return obj['Size']


def _get_schema_key(file_data):
    if 'id' in file_data:
        schema_id = file_data['id']
        key = schema_id.replace(".json", "")
        key = key.replace("https://schema.humancellatlas.org/", "")
        key = key.replace("https://schema.dev.humancellatlas.org/", "")
    else:
        key = None
    return key


def _send_notification(message, context, dryrun=False):
    if dryrun:
        print("DRY RUN:" + message)
    else:
        topic_name = os.environ['TOPIC_NAME']
        account_id = context.invoked_function_arn.split(":")[4]
        if account_id != "Fake":
            print("Sending notification to " + topic_name)
            topic_arn = "arn:aws:sns:" + os.environ['AWS_REGION'] + ":" + account_id + ":" + topic_name
            sns = boto3.client(service_name="sns")
            sns.publish(
                TopicArn=topic_arn,
                Message=message
            )
        else:
            print("Skipping notification: " + message)


def sns_to_slack(event, context):
    print(event)
    sns = event['Records'][0]['Sns']
    message = sns['Message']

    webhook_url = os.environ['SLACK_URL']

    payload = {
        'text': message
    }
    r = requests.post(webhook_url, json=payload)
    return r.status_code
