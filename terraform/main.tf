# AWS Specific variables
variable "aws_region" {
  type        = string
  description = "AWS Region to create the resource"
  default     = "us-east-1"
}

variable "aws_profile" {
  type        = string
  description = "AWS Profile to choose"
  default     = "default"
}

terraform {
  backend "s3" {
    bucket = "schema-humancellatlas-org-terraform"
    key    = "integration-schema-humancellatlas-org.tfstate"
    region = "us-east-1"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

