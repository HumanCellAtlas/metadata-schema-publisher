'use strict'
const git = require('simple-git')
const rimraf = require('rimraf')
const aws = require('aws-sdk')
const s3 = new aws.S3()
const fs = require('fs')

module.exports.onGithubRelease = (event, context, callback) => {
    let message = JSON.parse(event.body)
    let tag_name = message.release.tag_name
    let html_url = message.repository.html_url
    clone(tag_name, html_url, callback)
}

function clone(tag_name, html_url, callback) {
    require('lambda-git')().then(() => {
        let git_path = '/tmp/git'
        if (fs.existsSync(git_path)) {
            let url = html_url
            let local = '/tmp/repo'
            let cloneOptions = {}
            cloneOptions.checkoutBranch = tag_name
            rimraf(local, function() {
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

function copyToS3(local, tag_name, callback) {
    const bucket = process.env.BUCKET
    var dict = {};
    dict['cell_suspension.json'] = `module/biomaterial/${tag_name}/cell_suspension`;
    console.log('* Copying to bucket: ' + bucket)
    fs.readdir(local + '/json_schema', (err, files) => {
        files.forEach(file => {
            const path = local + '/json_schema/' + file
            if (!fs.lstatSync(path).isDirectory()) {
                const key = dict[file]
                if (key != null) {
                    fs.readFile(path, function(err, data) {
                        const params = { Bucket: bucket, Key: key, Body: data }
                        uploadFile(params)
                    })
                }
            }
        })
        finish(callback)
    })
}

function uploadFile(params) {
    console.log('Uploading ' + params.Key + ' to ' + params.Bucket)
    s3.upload(params, function(err, data) {
        if (err) {
            console.log('Error creating the file: ', err)
            callback(err, null)
        }
        else {
            console.log('Successfully creating ' + params.Key + ' on S3')
        }
    })
}

const index_html = "<html>\n" +
    "<head>\n" +
    "    <title>HCA Schema Repo</title>\n" +
    "</head>\n" +
    "<body>\n" +
    "<div id=\"listing\"></div>\n" +
    "\n" +
    "<script src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.9.0/jquery.min.js\"></script>\n" +
    "<script type=\"text/javascript\">\n" +
    "    var BUCKET_URL = 'http://schema.data.humancellatlas.org';\n" +
    "</script>\n" +
    "<script src=\"https://rufuspollock.github.io/s3-bucket-listing/list.js\"></script>\n" +
    "</body>\n" +
    "</html>"

function finish(callback) {
    const response = {
        statusCode: 200,
        body: JSON.stringify({}),
    }
    callback(null, response)
}
