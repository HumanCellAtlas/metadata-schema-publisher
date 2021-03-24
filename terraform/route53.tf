locals {
  route_53_hosted_zone = var.route53_hosted_zone
  domain = var.domain
}

data "aws_route53_zone" "main" {
  name = local.route_53_hosted_zone
  private_zone = false
}


resource "aws_route53_record" "app" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = local.domain
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.schema_cloudfront_dist.domain_name
    zone_id                = aws_cloudfront_distribution.schema_cloudfront_dist.hosted_zone_id
    evaluate_target_health = false
  }
}

resource "aws_route53_record" "cert_validation" {
  name    = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_name
  type    = tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_type
  zone_id = data.aws_route53_zone.main.id
  records = [tolist(aws_acm_certificate.cert.domain_validation_options)[0].resource_record_value]
  ttl     = 60
}

