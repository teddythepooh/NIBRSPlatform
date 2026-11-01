provider "aws" {
  region = var.AWS_REGION
}

variable "AWS_REGION" {
  type = string
  description = "AWS region"
}
variable "S3_BUCKET_NAME" {
  type = string
  description = "Name of S3 bucket"
}

resource "aws_s3_bucket" "nibrs" {
  bucket = var.S3_BUCKET_NAME
}
