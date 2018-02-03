'use strict';

module.exports.onGithubEvent = (event, context, callback) => {
  console.log(JSON.stringify(event))
  const response = {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Go Serverless v1.0! Your function executed successfully!',
      input: event,
    }),
  };

  callback(null, { message: 'Go Serverless v1.0! Your function executed successfully!', event });
};
