import base64
import json
import os
import time

import boto3
import jwt
import requests
from github import Github, GithubException

from metadata_schema import MetadataSchema, get_relative_url

BRANCH_REFS = ['refs/heads/master', 'refs/heads/staging', 'refs/heads/integration', 'refs/heads/develop']

BRANCH_CONFIG = {
    'develop': 'DEV_BUCKET',
    'integration': 'INTEGRATION_BUCKET',
    'staging': 'STAGING_BUCKET',
    'master': 'PROD_BUCKET'
}

INGEST_API = {
    'develop': 'https://api.ingest.dev.archive.data.humancellatlas.org',
    'integration': 'https://api.ingest.integration.archive.data.humancellatlas.org',
    'staging': 'https://api.ingest.staging.archive.data.humancellatlas.org',
    'main': 'https://api.ingest.archive.data.humancellatlas.org'
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


DEFAULT_JWT_AUDIENCE = 'https://dev.data.humancellatlas.org/'


def get_service_jwt(service_credentials, audience):
    iat = time.time()
    exp = iat + 3600
    payload = {'iss': service_credentials["client_email"],
               'sub': service_credentials["client_email"],
               'aud': audience,
               'iat': iat,
               'exp': exp,
               'scope': ["openid", "email", "offline_access"]
               }
    additional_headers = {'kid': service_credentials["private_key_id"]}
    signed_jwt = jwt.encode(payload, service_credentials["private_key"], headers=additional_headers,
                            algorithm='RS256').decode()
    return signed_jwt


def notify_ingest(branch_name, service_account):
    ingest_base_url = INGEST_API.get(branch_name)
    schema_update_url = f'{ingest_base_url}/schemas/update'

    audience = DEFAULT_JWT_AUDIENCE
    if branch_name == 'master':
        audience = "https://data.humancellatlas.org/"

    token = get_service_jwt(service_account, audience)
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.post(schema_update_url, headers=headers)
    r.raise_for_status()
    print('Notified Ingest!')


def get_access_token(secrets):
    access_token = secrets.get('GITHUB_ACCESS_TOKEN')
    if not access_token:
        raise Exception('A GitHub access token is required to communicate with GitHub API')
    return access_token


def get_service_account(secrets):
    service_account = secrets.get('GCP_SERVICE_ACCOUNT')
    if not service_account:
        raise Exception('A GCP service account is required to communicate with Ingest API')
    return json.loads(service_account)


def on_github_push(event, context, dryrun=False):
    message = _process_event(event)
    ref = message["ref"]
    secret_name = os.environ['SECRET_NAME']
    secrets = json.loads(get_secret(secret_name))
    access_token = get_access_token(secrets)
    service_account = get_service_account(secrets)

    if ref in BRANCH_REFS:
        repo_name = message["repository"]["full_name"]
        repo = Github(access_token).get_repo(repo_name)
        branch = repo.get_branch(ref)
        pusher = message["pusher"]["name"]
        notification_message = "Commit to " + ref + " detected on " + repo_name + " branch " + branch.name + " by " + \
                               pusher
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
            result_message = result_message + f"No schema changes published. Error count {len(errors)}"
        else:
            result_message = result_message + f"New schema changes published:\n{result_str}\nError count {len(errors)}"
            time.sleep(5)
            notify_ingest(branch.name, service_account)

        print(result_message)
        _send_notification(result_message, context, dryrun)

    else:
        result = []
        errors = []

    response = {
        "statusCode": 200,
        "body": json.dumps({
            "created": result,
            "errors": errors
        })
    }
    if is_dry_run():
        print("DRY RUN:" + json.dumps(response))
    return response


def _process_event(event):
    message = json.loads(event["body"])
    return message


def _process_directory(repo, branch_name, base_server_path, server_path, version_numbers, context, dryrun=False):
    print("Processing " + server_path + " in " + branch_name + " branch of " + repo.name)
    created_list = []
    error_list = []
    contents = repo.get_dir_contents(server_path, branch_name)
    for content in contents:
        if content.type == 'dir':
            created_list.extend(
                _process_directory(repo, branch_name, base_server_path, content.path, version_numbers, context, dryrun))
        else:
            try:
                path = content.path
                file_root, file_extension = os.path.splitext(path)
                if path.endswith('versions.json') or path.endswith('.md'):
                    print("- skipping: " + path)
                else:
                    print("- processing: " + path)
                    file_content = repo.get_contents(path, branch_name)
                    data = base64.b64decode(file_content.content)
                    json_data = json.loads(data.decode('utf8'))
                    relative_path = path.replace(base_server_path + "/", "")
                    relative_path = relative_path.replace(".json", "")
                    key = None

                    if relative_path in UNVERSIONED_FILES:
                        key = relative_path
                    else:
                        schema_base_url = SCHEMA_URL.get(branch_name)
                        metadata_schema = MetadataSchema(json_data, relative_path)
                        json_data = metadata_schema.get_json_schema(version_numbers, schema_base_url)
                        key = get_relative_url(relative_path, version_numbers)

                    if key is None:
                        print("- could not find key for: " + path)
                    else:
                        created = _upload(key, branch_name, json_data, context, dryrun)
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
                              ContentType='application/json', CacheControl="no-cache")
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

    secret_name = os.environ['SECRET_NAME']
    secret = get_secret(secret_name)
    secrets = json.loads(secret)

    webhook_url = secrets.get('SLACK_URL')

    if not webhook_url:
        raise Exception('Could not find the slack webhook url!')

    payload = {
        'text': message
    }
    r = requests.post(webhook_url, json=payload)
    return r.status_code


def get_secret(secret_name, region_name=None):
    if not region_name:
        region_name = os.environ['AWS_PROVIDER_REGION']

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    else:
        return base64.b64decode(get_secret_value_response['SecretBinary'])
