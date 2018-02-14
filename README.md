## Run Locally

[Run a function locally](https://serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/#)
```
serverless invoke local --function functionName 
```

### Simulate a github event

```
serverless invoke local --function onGithubRelease --path ./tests/files/github-event-release.json
```

### Invoke
```
serverless invoke --function onGithubRelease --path ./examples/github-event-release.json --aws-profile secondary-hca-profile

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
