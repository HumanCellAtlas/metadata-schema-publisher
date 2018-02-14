import json
import shutil
from git import Repo, GitCommandError

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
    release = {}
    release["tag_name"] = message["release"]["tag_name"]
    release["repo_url"] = message["repository"]["html_url"]
    return release

def clone_repo(repo_url, local_path):
    #repo = {}
    #repo["remote_url"] = release["repo_url"]
    #repo["local_path"] = local_path
    #Repo.clone_from(repo["remote_url"], local_path)
    #return repo
    try:
        clear_local_path(local_path)
        Repo.clone_from(repo_url, local_path)
    except GitCommandError as error:
        notify_of_error(error)
        
    
def clear_local_path(local_path):
    shutil.rmtree(local_path)
    
def notify_of_error(error):
    print(error)
