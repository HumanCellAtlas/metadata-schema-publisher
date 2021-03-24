variable "bucket_name" {
  type        = string
  description = "The Fully Qualified domain name should be the bucket name"
  default     = ""
}

variable "route53_hosted_zone" {
  type        = string
  description = "Route53 hostedzone name"
  default     = ""
}

variable "domain" {
  type        = string
  description = "simple website where route53 hosted zone and bucket name are same. Naked domain"
  default     = ""
}

variable "index_document" {
  type        = string
  description = "Index page to be used for website. Defaults to index.html"
  default     = "index.html"
}

variable "error_document" {
  type        = string
  description = "Error page to be used for website. Defaults to error.html"
  default     = "error.html"
}

variable "env" {
  type        = string
  description = "Deployment environment"
  default     = "integration"
}