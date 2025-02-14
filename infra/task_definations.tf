# LLM GYM Service
resource "aws_ecs_task_definition" "fastapi_app" {
  family                   = "fastapi-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "1024"
  memory                   = "2048"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([
    {
      name      = "fastapi-app"
      image     = "418721317505.dkr.ecr.us-east-1.amazonaws.com/gym_reader:2025.01.19-154657"
      essential = true
      portMappings = [
        {
          containerPort = 8000
          hostPort      = 8000
          protocol      = "tcp"
        }
      ]
  environment = [
    {
          name  = "ENVIRONMENT"
          value = "DEV"
        },
        {
          name  = "APP_NAME"
          value = "gym_reader"
        },
        {
          name  = "QDRANT_URL"
          value = "http://qdrant.lmgym.com"
        },
        {
          name  = "QDRANT_PORT"
          value = "6333"
        },
        {
          name  = "TOKEN_KEY"
          value = "X-Total-LLM-Tokens"
        },
        {
          name  = "CONFIG_FILE_PATH"
          value = "gym_reader/config.yml"
        },
        {
          name  = "MEILISEARCH_MASTER_KEY"
          value = "aSampleMasterKey"
        },
        {
          name  = "MEILISEARCH_URL"
          value = "http://mili.lmgym.com:7700"
        },
        {
          name  = "REDIS_HOST"
          value = "redis-10247.c244.us-east-1-2.ec2.redns.redis-cloud.com"
        },
        {
          name  = "REDIS_PORT"
          value = "10247"
        }
      ]
      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_secretsmanager_secret.openai_api_key.arn
        },
        {
          name      = "MEILISEARCH_API_KEY"
          valueFrom = aws_secretsmanager_secret.meilisearch_api_key.arn
        },
        {
          name      = "PAT_TOKEN"
          valueFrom = aws_secretsmanager_secret.pat_token.arn
        },
        {
          name      = "TAVILY_API_KEY"
          valueFrom = aws_secretsmanager_secret.tavily_api_key.arn
        },
        {
          name      = "SPIDER_API_KEY"
          valueFrom = aws_secretsmanager_secret.spider_api_key.arn
        },
        {
          name      = "DIRECT_URL"
          valueFrom = aws_secretsmanager_secret.direct_url.arn
        },
        {
          name      = "GITHUB_SECRET_KEY_FOR_WEBHOOK"
          valueFrom = aws_secretsmanager_secret.github_secret_key_for_webhook.arn
        },
        {
          name      = "REDIS_PASSWORD"
          valueFrom = aws_secretsmanager_secret.redis_password.arn
        }

      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/fastapi-app"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# QDRANT Service
resource "aws_ecs_task_definition" "qdrant" {
  family                   = "qdrant"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "qdrant"
      image     = "qdrant/qdrant:latest" # use public image 
      essential = true
      portMappings = [
        {
          containerPort = 6333
          hostPort      = 6333
          protocol      = "tcp"
        }
      ]
      mountPoints = [
        {
          sourceVolume  = "qdrant-data"
          containerPath = "/qdrant/storage"
          readOnly      = false
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/qdrant"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
  volume {
    name = "qdrant-data"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.qdrant_fs.id
      root_directory          = "/"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = null
        iam             = "DISABLED"
      }
    }
  }
}

# Meilisearch Service
resource "aws_ecs_task_definition" "meilisearch" {
  family                   = "meilisearch"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "meilisearch"
      image     = "getmeili/meilisearch:v1.10" # use public image 
      essential = true
      portMappings = [
        {
          containerPort = 7700
          hostPort      = 7700
          protocol      = "tcp"
        }
      ]
      mountPoints = [
        {
          sourceVolume  = "meilisearch-data"
          containerPath = "/meili_data"
          readOnly      = false
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/meilisearch"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
  volume {
    name = "meilisearch-data"
    efs_volume_configuration {
      file_system_id          = aws_efs_file_system.meilisearch_fs.id
      root_directory          = "/"
      transit_encryption      = "ENABLED"
      authorization_config {
        access_point_id = null
        iam             = "DISABLED"
      }
    }
  }
}

resource "aws_ecs_task_definition" "search_ui" {
  family                   = "search-ui"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn

  container_definitions = jsonencode([
    {
      name      = "search-ui"
      image     = "418721317505.dkr.ecr.us-east-1.amazonaws.com/search-ui:2024.12.04-190903" # I will replace it later
      essential = true
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "REACT_APP_API_BASE_URL" // App Base URL
          value = "https://api.lmgym.com"
        }
      ]
      secrets = [
        {
          name      = "REACT_APP_SECRET_KEY_FOR_API"
          valueFrom = aws_secretsmanager_secret.github_secret_key_for_webhook.arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/search-ui"
          awslogs-region        = var.region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}