import base64
import json
import os
import requests

import boto3
from github import Github, GithubException


def on_github_push(event, context):
    repo_name = _process_event(event)
    api_key = os.environ['API_KEY']
    repo = Github(api_key).get_repo(repo_name)
    _send_notification("Commit detected on " + repo_name, context)
    result = _process_directory(repo, 'json_schema')
    result_str = "\n".join(result)
    if len(result) == 0:
        message = "No schema changes published"
    else:
        message = "New schema changes published:\n" + result_str
    _send_notification(message, context)
    response = {
        "statusCode": 200,
        "body": {
            "created": json.dumps(result)
        }
    }
    return response


def _process_event(event):
    message = json.loads(event["body"])
    return message["repository"]["full_name"]


def _process_directory(repo, server_path):
    print("Processing " + server_path + " in " + repo.name)
    created_list = []
    branch = repo.get_branch('v5_prototype')
    sha = branch.commit.sha
    contents = repo.get_dir_contents(server_path, ref=sha)
    for content in contents:
        if content.type == 'dir' and ("bundle" not in content.path):
            created_list.extend(_process_directory(repo, content.path))
        else:
            try:
                path = content.path
                file_root, file_extension = os.path.splitext(path)
                if file_extension == '.json':
                    print("- processing: " + path)
                    file_content = repo.get_contents(path, ref=sha)
                    file_data = base64.b64decode(file_content.content)
                    key = _get_schema_key(file_data)
                    created = _upload(key, file_data)
                    if created:
                        created_list.append(key)
                else:
                    print("- skipping: " + path)
            except(GithubException, IOError) as e:
                print('Error processing %s: %s', content.path, e)
    return created_list


def _upload(key, file_data):
    bucket = os.environ['BUCKET']
    s3 = boto3.client('s3')
    if not _key_exists(s3, bucket, key):
        try:
            s3.put_object(Bucket=bucket, Key=key, Body=file_data, ACL='public-read')
            return True
        except Exception as e:
            print('Error uploading ' + key, e)
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
    file_json = json.loads(file_data)
    schema_id = file_json['id']
    key = schema_id.replace(".json", "")
    key = key.replace("http://schema.humancellatlas.org/", "")
    return key


def _send_notification(message, context):
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
