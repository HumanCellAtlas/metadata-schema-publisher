import base64
import boto3
import json
import os
import requests

from github import Github, GithubException

from release_prep import ReleasePreparation

BRANCH_REFS = ['refs/heads/master', 'refs/heads/staging', 'refs/heads/integration', 'refs/heads/develop']

BRANCH_CONFIG = {
    'develop': 'DEV_BUCKET',
    'integration': 'INTEGRATION_BUCKET',
    'staging': 'STAGING_BUCKET',
    'master': 'PROD_BUCKET'
}

INGEST_API = {
    'develop': 'https://api.ingest.dev.data.humancellatlas.org',
    'integration': 'https://api.ingest.integration.data.humancellatlas.org',
    'staging': 'https://api.ingest.staging.data.humancellatlas.org',
    'master': 'https://api.ingest.data.humancellatlas.org'
}

SCHEMA_URL = {
    'master': 'https://schema.humancellatlas.org/',
    'develop': 'https://schema.dev.data.humancellatlas.org/',
    'integration': 'https://schema.integration.data.humancellatlas.org/',
    'staging': 'https://schema.staging.data.humancellatlas.org/'

}

UNVERSIONED_FILES = [
    'property_migrations'
]


def _notify_ingest(branch_name):
    ingest_base_url = INGEST_API.get(branch_name)
    schema_update_url = f'{ingest_base_url}/schemas/update'
    r = requests.post(schema_update_url)
    r.raise_for_status()
    print('Notified Ingest!')


def on_github_push(event, context, dryrun=False):
    message = _process_event(event)
    ref = message["ref"]

    if ref in BRANCH_REFS:
        api_key = os.environ['API_KEY']
        repo_name = message["repository"]["full_name"]
        repo = Github(api_key).get_repo(repo_name)
        branch = repo.get_branch(ref)
        pusher = message["pusher"]["name"]
        notification_message = "Commit to " + ref + " detected on " + repo_name + " branch " + branch.name + " by " + pusher
        print(notification_message)
        _send_notification(notification_message, context, dryrun)
        server_path = 'json_schema'
        versions_file = repo.get_contents(server_path + "/versions.json", branch.name)
        version_numbers_str = base64.b64decode(versions_file.content).decode("utf-8")
        version_numbers = json.loads(version_numbers_str)

        result = _process_directory(repo, branch.name, server_path, server_path, version_numbers, context, dryrun)
        result_str = "\n".join(result)
        result_message = ""

        if len(result) == 0:
            result_message = result_message + "No schema changes published"
        else:
            result_message = result_message + "New schema changes published:\n" + result_str
            _notify_ingest(branch.name)
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


def _process_directory(repo, branch_name, base_server_path, server_path, version_numbers, context, dryrun=False):
    print("Processing " + server_path + " in " + branch_name + " branch of " + repo.name)
    created_list = []
    contents = repo.get_dir_contents(server_path, branch_name)
    for content in contents:
        if content.type == 'dir':
            created_list.extend(
                _process_directory(repo, branch_name, base_server_path, content.path, version_numbers, context, dryrun))
        else:
            try:
                path = content.path
                file_root, file_extension = os.path.splitext(path)
                if file_extension == '.json' and not path.endswith('versions.json'):
                    print("- processing: " + path)
                    file_content = repo.get_contents(path, branch_name)
                    data = base64.b64decode(file_content.content)
                    json_data = json.loads(data.decode('utf8'))
                    relative_path = path.replace(base_server_path + "/", "")
                    relative_path = relative_path.replace(".json", "")
                    key = None

                    if relative_path in UNVERSIONED_FILES:
                        expanded_file_data = json_data
                        key = relative_path
                    else:
                        schema_url = SCHEMA_URL.get(branch_name)
                        release_preparation = ReleasePreparation(schema_url=schema_url, version_map=version_numbers)
                        expanded_file_data = release_preparation.expand_urls(relative_path, json_data)
                        key = release_preparation.get_schema_key(expanded_file_data)

                    if key is None:
                        print("- could not find key for: " + path)
                    else:
                        created = _upload(key, branch_name, expanded_file_data, context, dryrun)
                        if created:
                            created_list.append(key)
                else:
                    print("- skipping: " + path)
            except(GithubException, IOError) as e:
                print('Error processing %s: %s', content.path, e)
    return created_list


def _upload(key, branch_name, file_data, context, dryrun=False):
    if dryrun:
        output_dir = 'dryrun'
        output_path = output_dir + '/' + key
        pos = output_path.rfind('/')
        os.makedirs(output_path[0:pos], exist_ok=True)
        with open(output_path, 'w') as outfile:
            json.dump(file_data, outfile, indent=2)
        print("Output: " + output_path)
        return True
    else:
        bucket_env_var = BRANCH_CONFIG.get(branch_name)

        bucket = os.environ[bucket_env_var]

        s3 = boto3.client('s3')

        if (not _key_exists(s3, bucket, key)) or (key in UNVERSIONED_FILES):
            try:
                s3.put_object(Bucket=bucket, Key=key, Body=json.dumps(file_data, indent=2),
                              ContentType='application/json', ACL='public-read', CacheControl="no-cache")
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
