resource "aws_cloudfront_distribution" "schema_cloudfront_dist" {
  http_version = "http2"

  origin {
    origin_id   = "origin-${local.bucket_name}"
    domain_name = aws_s3_bucket.schema_bucket.bucket_domain_name

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.origin_access_identity.cloudfront_access_identity_path
    }

  }

  enabled             = true
//  default_root_object = var.index_document

  aliases = concat([local.domain])

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  default_cache_behavior {
    target_origin_id = "origin-${local.bucket_name}"
    allowed_methods  = ["GET", "HEAD"]
    cached_methods   = ["GET", "HEAD"]
    compress         = true

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 300
    max_ttl                = 1200
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate_validation.cert.certificate_arn
    cloudfront_default_certificate = false
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2019"
  }
}

resource "aws_cloudfront_origin_access_identity" "origin_access_identity" {
  comment = "${local.bucket_name}-origin-access-identity"
}