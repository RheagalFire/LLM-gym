resource "aws_cloudwatch_log_group" "fastapi_log_group" {
  name              = "/ecs/fastapi-app"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "qdrant_log_group" {
  name              = "/ecs/qdrant"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "meilisearch_log_group" {
  name              = "/ecs/meilisearch"
  retention_in_days = 7
}
