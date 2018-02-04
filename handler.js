'use strict'
const Git = require('nodegit')
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
  require('lambda-git')()
  let url = html_url
  let local = '/tmp/repo'
  let cloneOptions = {}
  cloneOptions.checkoutBranch = tag_name
  rimraf(local, function () {
    console.log('* Removed existing: ' + local)
    console.log('* Cloning: ' + url + ' tag: ' + tag_name)
    Git.Clone(url, local).then(function (repo) {
      console.log('* Cloned: ' + url + 'to ' + local)
      copyToS3(local, tag_name, callback)
    }).catch(function (err) {
      callback(err, null)
    })
  })
}

function copyToS3 (local, tag_name, callback) {
  const params = {Bucket: 'schema.data.humancellatlas.org', Key: 'tag_name', ACL: 'public-read', Body: ''}
  upload(params)
  fs.readdir(local + '/json_schema', (err, files) => {
    files.forEach(file => {
      fs.readFile(local + '/json_schema/' + file, function (err, data) {
        var param = {Bucket: 'schema.data.humancellatlas.org/' + tag_name, Key: file, Body: data}
        console.log(param)
      })
    })
  })
  finish(callback)
}

function upload(params) {
  s3.upload(params, function (err, data) {
    if (err) {
      console.log('Error creating the file: ', err)
      callback(err, null)
    } else {
      console.log('Successfully created a folder on S3')
      f
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