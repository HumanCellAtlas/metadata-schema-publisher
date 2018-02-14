import json
import shutil
import base64
import logging
import os
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
                filename, file_extension = os.path.splitext(path)
                if (file_extension=='.json'):
                    file_content = repo.get_contents(path, ref=sha)
                    file_data = base64.b64decode(file_content.content)
                    print("path:" + path)
                    schema_version = get_schema_key(file_data)
                    print(schema_version)
                    upload(path)
            except(GithubException, IOError) as e:
                logging.error('Error processing %s: %s', content.path, e)

def upload(path):
    print ("File: " + path)
    
def get_schema_key(file_data):
    file_json = json.loads(file_data)
    return file_json['id']