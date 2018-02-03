## Run Locally

[Run a function locally](https://serverless.com/framework/docs/providers/aws/cli-reference/invoke-local/#)
```
serverless invoke local --function functionName 
```

### Simulate a github event

```
serverless invoke local --function onGithubEvent --path ./examples/github-event.json
```