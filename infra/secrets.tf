resource "aws_secretsmanager_secret" "openai_api_key" {
  name        = "openai_api_key"
  description = "OpenAI API Key for FastAPI App"
}

resource "aws_secretsmanager_secret_version" "openai_api_key_version" {
  secret_id     = aws_secretsmanager_secret.openai_api_key.id
  secret_string = var.openai_api_key
}

resource "aws_secretsmanager_secret" "meilisearch_api_key" {
  name        = "meilisearch_api_key"
  description = "Meilisearch API Key for FastAPI App"
}

resource "aws_secretsmanager_secret_version" "meilisearch_api_key_version" {
  secret_id     = aws_secretsmanager_secret.meilisearch_api_key.id
  secret_string = var.meilisearch_api_key
}

resource "aws_secretsmanager_secret" "pat_token" {
  name        = "pat_token"
  description = "Personal Access Token for FastAPI App"
}

resource "aws_secretsmanager_secret_version" "pat_token_version" {
  secret_id     = aws_secretsmanager_secret.pat_token.id
  secret_string = var.pat_token
}

resource "aws_secretsmanager_secret" "tavily_api_key" {
  name        = "tavily_api_key"
  description = "Tavily API Key for FastAPI App"
}

resource "aws_secretsmanager_secret_version" "tavily_api_key_version" {
  secret_id     = aws_secretsmanager_secret.tavily_api_key.id
  secret_string = var.tavily_api_key
}

resource "aws_secretsmanager_secret" "spider_api_key" {
  name        = "spider_api_key"
  description = "Spider API Key for FastAPI App"
}

resource "aws_secretsmanager_secret_version" "spider_api_key_version" {
  secret_id     = aws_secretsmanager_secret.spider_api_key.id
  secret_string = var.spider_api_key
}

resource "aws_secretsmanager_secret" "direct_url" {
  name        = "direct_url"
  description = "Direct URL for FastAPI App"
}

resource "aws_secretsmanager_secret" "github_secret_key_for_webhook" {
  name        = "github_secret_key_for_webhook"
  description = "GitHub Secret Key for Webhook"
}
