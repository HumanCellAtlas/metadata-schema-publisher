## Run Locally

[Run a function locally](https://serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/#)
```
serverless invoke local --function functionName 
```

### Simulate a github event

```
serverless invoke local --function onGithubEvent --path ./examples/github-event.json
```

### Suggested Logic

If a new tag has been created e.g.
```
"ref\":\"refs/tags/github-test\",\"before\":\"0000000000000000000000000000000000000000\"
```

Check out that tag and copy the content of json_schema into a new s3 directory with the same name as the tag.

- Use something like this for do git clone into /tmp https://github.com/nodegit/nodegit
- Copy files into S3
```
   var s3 = new AWS.S3();
   s3.putObject(params).promise()
```
- Remove files from tmp
