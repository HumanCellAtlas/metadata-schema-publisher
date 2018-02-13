import json

def on_github_release(event, context):
    process_event(event)
    response = {
        "statusCode": 200,
        "body": ""
    }
    return response
    
def process_event(event):
    message = json.loads(event["body"])
    print(message)
    tag_name = message["release"]["tag_name"]
    html_url = message["repository"]["html_url"]
    print("tag_name: " + tag_name)
