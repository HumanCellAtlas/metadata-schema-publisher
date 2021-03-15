#!/usr/bin/env bash

DEPLOYMENT_STAGE=$1

TF_VAR_terraform_key="schema/${DEPLOYMENT_STAGE}-schema.tfstate"
TF_VAR_aws_profile=${AWS_PROFILE}
TF_VAR_deployment_stage=${DEPLOYMENT_STAGE}
TF_VAR_aws_region=us-east-1
TF_VAR_terraform_bucket=schema-terraform


[[ -d .terraform ]] || terraform init \
  -backend-config="bucket=$TF_VAR_terraform_bucket" \
  -backend-config="profile=$TF_VAR_aws_profile" \
  -backend-config="region=$TF_VAR_aws_region" \
  -backend-config="key=$TF_VAR_terraform_key"

