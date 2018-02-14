import json
import shutil
from github import Github

def on_github_release(event, context):
    release = process_event(event)
    local_path = "/tmp/repo"
    repo = clone_repo(release, local_path)
    result = {}
    result["release"] = release
    result["repo"] = repo
    response = {
        "statusCode": 200,
        "body": result
    }
    return response
    
def process_event(event):
    message = json.loads(event["body"])
    return message["repository"]["full_name"]


