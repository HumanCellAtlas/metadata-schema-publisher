locals {
  bucket_name = var.bucket_name
}

resource "aws_s3_bucket" "schema_bucket" {
  bucket = local.bucket_name
  acl    = "private"
  policy = data.aws_iam_policy_document.s3_policy.json

  force_destroy = "false"

  tags = {
    "Name" = local.bucket_name
  }
}

data "aws_iam_policy_document" "s3_policy" {
  statement {
    sid = "AllowGetFromOriginAccessIdentity"

    actions = [
      "s3:GetObject",
    ]

    resources = [
      "arn:aws:s3:::${local.bucket_name}/*",
    ]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.origin_access_identity.iam_arn]
    }
  }

  statement {
    sid = "AllowListFromOriginAccessIdentity"

    actions = [
      "s3:ListBucket",
    ]

    resources = [
      "arn:aws:s3:::${local.bucket_name}",
    ]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.origin_access_identity.iam_arn]
    }
  }

}

# Refactor it to use loop
resource "aws_s3_bucket_object" "index" {
  bucket       = local.bucket_name
  key          = "index.html"
  source       = "../client/index.html"
  content_type = "text/html"
}
