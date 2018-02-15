# Metadata Schema Publisher

## Setup

### Install NodeJS dependencies
Run:
```
npm install
```
To install required node libraries. Even though the Lambdas are written in Python the framework is in NodeJS and it needs extra plugins.

### Install Python dependencies
Run:
```
pip install -r requirements.txt
```

## Run Locally

[Run a function locally](https://serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/#)

Run with a simulated GitHub event:

```
serverless invoke local --function onGithubPush --path ./tests/files/github-event-push.json
```

## Invoke on AWS
```
serverless invoke --function onGithubPush --path ./tests/files/github-event-push.json

```
## Deploy
```
serverless deploy -v
```

### Suggested Logic
On github [release](https://developer.github.com/v3/activity/events/types/#releaseevent) event

AWS SNS is an integration rather than a webhook and it seems to receive only push events as opposed to webhooks where we could filter purely on a release

If a new tag has been created e.g.
```
"ref\":\"refs/tags/github-test\",\"before\":\"0000000000000000000000000000000000000000\"
```

Check out that tag and copy the content of json_schema into a new s3 directory with the same name as the tag.

- Use something like this for do git clone into /tmp https://github.com/nodegit/nodegit
    - Lambda does not have git installed so try require("lambda-git")(); which installs a git binary on lambda
- Copy files into S3
```
   var s3 = new AWS.S3();
   s3.putObject(params).promise()
```
- Remove files from tmp


## TODO
- ~~Update README.md~~
- ~~Remove JavaScript~~
- ~~Rename project to something starting metadata~~
- ~~Change region of deployment~~
- Change to actual Github repo
- ~~Chnage to schema.humancellatlas.org bucket~~
- ~~Change to responding to commits instead of releases~~
- Add Slack notifications to a HCA slack channel
    - For triggered
    - For results
    - Using [https://github.com/robbwagoner/aws-lambda-sns-to-slack](https://github.com/robbwagoner/aws-lambda-sns-to-slack)
- Consider adding CloudFront (with 5 min cache)
    