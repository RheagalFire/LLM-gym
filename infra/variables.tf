variable "region" {
  description = "AWS Region to deploy resources"
  default     = "us-east-1"
}
variable "qdrant_host_header" {
  description = "Host header for the Qdrant service"
  default     = "qdrant.lmgym.com"
}
variable "meilisearch_host_header" {
  description = "Host header for the Meilisearch service"
  default     = "mili.lmgym.com"
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
  default     = "arn:aws:acm:us-east-1:418721317505:certificate/e6e3aaf3-a596-4571-9122-0a5c1cee88b6"
}

variable "additional_certificate_arn" {
  description = "ARN of the additional certificate for the domain"
  type        = string
  default     = "arn:aws:acm:us-east-1:418721317505:certificate/fd513178-d939-4608-b55c-af65f488ce3f"
}

variable "github_secret_key_for_webhook" {
  description = "GitHub Secret Key for Webhook"
  type        = string
  sensitive   = true
}

variable "direct_url" {
  description = "Direct URL for FastAPI App"
  type        = string
  sensitive   = true
}

variable "private_subnet_cidr_1" {
  description = "CIDR block for the private subnet 1"
  default     = "10.0.5.0/24"
}

variable "private_subnet_cidr_2" {
  description = "CIDR block for the private subnet 2"
  default     = "10.0.6.0/24"
}

variable "search_ui_host_header" {
  description = "Host header for the Search UI service"
  default     = "lmgym.com"
}

variable "api_service_host_header" {
  description = "Host header for the API service"
  default     = "api.lmgym.com"
}

variable "redis_password" {
  description = "Redis Password for FastAPI App"
  type        = string
  sensitive   = true
}
