variable "region" {
  description = "AWS Region to deploy resources"
  default     = "us-east-1"
}

variable "aws_account_id" {
  description = "Your AWS Account ID"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr_1" {
  description = "CIDR block for the public subnet 1"
  default     = "10.0.3.0/24"
}

variable "public_subnet_cidr_2" {
  description = "CIDR block for the public subnet 2"
  default     = "10.0.4.0/24"
}

variable "availability_zone" {
  description = "Availability zone for the subnet"
  default     = "us-east-1a"
}

variable "availability_zone_2" {
  description = "Availability zone 2 for the subnet"
  default     = "us-east-1b"
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "meilisearch_api_key" {
  description = "Meilisearch API Key"
  type        = string
  sensitive   = true
}

variable "pat_token" {
  description = "Personal Access Token"
  type        = string
  sensitive   = true
}

variable "tavily_api_key" {
  description = "Tavily API Key"
  type        = string
  sensitive   = true
}

variable "spider_api_key" {
  description = "Spider API Key"
  type        = string
  sensitive   = true
}

variable "certificate_arn" {
  description = "ARN of the certificate for the domain"
  type        = string
  default     = "arn:aws:acm:us-east-1:418721317505:certificate/fd513178-d939-4608-b55c-af65f488ce3f"
}
