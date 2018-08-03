# Metadata Schema Publisher

Automatically publishes metadata schemas to [schema.humacellatlas.org](https://schema.humancellatlas.org) when changes are made to the [GitHub repo](https://github.com/HumanCellAtlas/metadata-schema).

## Architecture
![Architecture of schema.humancellatlas.org metadata publisher](schema.humancellatlas.org.png)

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
serverless invoke local --function onGithubPush --path ./tests/files/mock-event.json
```

## Invoke on AWS
```
serverless invoke --function onGithubPush --path ./tests/files/github-event-push.json

```
## Deploy
```
serverless deploy -v
```

## Current Deployment

[metadata-schema-publisher-prod-onGithubPush](https://console.aws.amazon.com/lambda/home?region=us-east-1#/functions/metadata-schema-publisher-prod-onGithubPush?tab=graph)
`

###Logic

- On GitHub [push](https://developer.github.com/v3/activity/events/types/#pushevent) event from [WebHook](https://github.com/HumanCellAtlas/metadata-schema/settings/hooks)
- Go through all files ending with .json in the json_schema folder in the rep and update content to reflect latest versions in version.json
- Check the id field in each schema and use that as the key of S3
- Check if the S3 key exists and if not upload the file
- Send notifications for when the process starts and a summary when it finishes

## Setting up new schema environments
See notes: https://docs.google.com/document/d/1FQo9ofrFTSqLKx2a6eCHqTIpJxhAtShlCVkx6j6yA6s/edit