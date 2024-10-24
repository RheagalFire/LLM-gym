# LLM GYM Service
resource "aws_ecs_task_definition" "fastapi_app" {
  family                   = "fastapi-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  container_definitions = jsonencode([
    {
      name      = "fastapi-app"
      image     = "418721317505.dkr.ecr.us-east-1.amazonaws.com/llm-gym-app:v2" # I will replace it later
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
          name  = "QDRANT_HOST"
          value = "qdrant"
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
          name  = "REACT_APP_API_BASE_URL"
          value = "http://localhost:8001"
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
      image     = "418721317505.dkr.ecr.us-east-1.amazonaws.com/search-ui:latest" # I will replace it later
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
          value = "http://localhost:8000"
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