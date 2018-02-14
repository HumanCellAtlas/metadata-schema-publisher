import base64
import json
import logging
import os

import boto3
from github import Github, GithubException


def on_github_release(event, context):
    repo_name = process_event(event)
    repo = Github("0a43698e4acb763d4713f2e1765a0d7622ab26be").get_repo(repo_name)
    traverse_repository(repo, 'json_schema')
    response = {
        "statusCode": 200,
        "body": ""
    }
    return response


def process_event(event):
    message = json.loads(event["body"])
    return message["repository"]["full_name"]


def traverse_repository(repo, server_path):
    process_directory(repo, server_path)


def process_directory(repo, server_path):
    branch = repo.get_branch('v5_prototype')
    sha = branch.commit.sha
    contents = repo.get_dir_contents(server_path, ref=sha)
    for content in contents:
        if content.type == 'dir' and ("bundle" not in content.path):
            process_directory(repo, content.path)
        else:
            try:
                path = content.path
                file_root, file_extension = os.path.splitext(path)
                if file_extension == '.json':
                    file_content = repo.get_contents(path, ref=sha)
                    file_data = base64.b64decode(file_content.content)
                    key = get_schema_key(file_data)
                    upload(key, file_data)
            except(GithubException, IOError) as e:
                logging.error('Error processing %s: %s', content.path, e)


def upload(key, file_data):
    bucket_name = os.environ['BUCKET']
    s3 = boto3.client('s3')
    #bucket = s3.Bucket(bucket_name)
    print("bucket: " + bucket_name + ", key: " + key)
    if not _key_exists(s3, bucket_name, key):
        s3.put_object(Bucket=bucket_name, Key=key, Body=file_data)
        print("- created")
    else:
        print("- already exists")


def _key_exists(s3, bucket, key):
    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )
    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return obj['Size']


def get_schema_key(file_data):
    file_json = json.loads(file_data)
    schema_id = file_json['id']
    key = schema_id.replace(".json", "")
    key = key.replace("http://schema.humancellatlas.org", "")
    return key
