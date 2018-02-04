'use strict'
const git = require('simple-git')
const rimraf = require('rimraf')
const aws = require('aws-sdk')
const s3 = new aws.S3()
const fs = require('fs')

module.exports.onGithubEvent = (event, context, callback) => {
  let sns = event.Records[0].Sns
  let notification = JSON.parse(sns.Message)
  console.log(notification)
  const response = {
    statusCode: 200,
    body: JSON.stringify({
      message: 'Go Serverless v1.0! Your function executed successfully!',
      input: event,
    }),
  }

  callback(null, {message: 'Go Serverless v1.0! Your function executed successfully!'})
}

module.exports.onGithubRelease = (event, context, callback) => {
  let message = JSON.parse(event.body)
  let tag_name = message.release.tag_name
  let html_url = message.repository.html_url
  clone(tag_name, html_url, callback)
}

function clone (tag_name, html_url, callback) {
  require('lambda-git')().then(() => {
    let git_path = '/tmp/git'
    if (fs.existsSync(git_path)) {
      let url = html_url
      let local = '/tmp/repo'
      let cloneOptions = {}
      cloneOptions.checkoutBranch = tag_name
      rimraf(local, function () {
        console.log('* Removed existing: ' + local)
        console.log('* Cloning: ' + url + ' tag: ' + tag_name)
        git().clone(url, local)
          .then(() => {
            console.log('* Cloned: ' + url + 'to ' + local)
            copyToS3(local, tag_name, callback)
          })
      })
    }
    else {
      fs.readdir('/tmp/', (err, files) => {
        console.log(files)
      })
      const response = {
        statusCode: 500,
        body: JSON.stringify({
          message: git_path + ' does not exist'
        }),
      }
      callback(null, response)
    }
  })
}

function copyToS3 (local, tag_name, callback) {
  const bucket = process.env.BUCKET
  console.log('* Copying to bucket: ' + bucket)
  fs.readdir(local + '/json_schema', (err, files) => {
    files.forEach(file => {
      const path = local + '/json_schema/' + file
      if (!fs.lstatSync(path).isDirectory()) {
        fs.readFile(path, function (err, data) {
          const params = {Bucket: bucket, Key: tag_name + '/' + file, Body: data}
          uploadFile(params)
        })
      }
    })
    finish(callback)
  })
}

function uploadFile (params) {
  console.log('Uploading ' + params.Key + ' to ' + params.Bucket)
  s3.upload(params, function (err, data) {
    if (err) {
      console.log('Error creating the file: ', err)
      callback(err, null)
    } else {
      console.log('Successfully creating ' + params.Key + ' on S3')
    }
  })
}

function finish (callback) {
  const response = {
    statusCode: 200,
    body: JSON.stringify({}),
  }
  callback(null, response)
}