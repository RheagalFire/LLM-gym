resource "aws_ecs_service" "fastapi_app" {
  name            = "fastapi-app-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }
  // Service discovery for fastapi-app
  # service_registries {
  #   registry_arn = aws_service_discovery_service.fastapi_app_service_discovery.arn
  # }
  
  # Add Load Balancer Mapping here
  load_balancer {
    target_group_arn = aws_lb_target_group.api_service_tg.arn
    container_name   = "fastapi-app"
    container_port   = 8000
  }
  depends_on = [aws_lb_listener.http, aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
#
resource "aws_ecs_service" "qdrant" {
  name            = "qdrant-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.qdrant.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }
  # Add Load Balancer Mapping here
  load_balancer {
    target_group_arn = aws_lb_target_group.qdrant_tg.arn
    container_name   = "qdrant"
    container_port   = 6333
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
resource "aws_ecs_service" "meilisearch" {
  name            = "meilisearch-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.meilisearch.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = false
  }
  # Add Load Balancer Mapping here
  load_balancer {
    target_group_arn = aws_lb_target_group.meilisearch_tg.arn
    container_name   = "meilisearch"
    container_port   = 7700
  }
}
resource "aws_ecs_service" "search_ui" {
  name            = "search-ui-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.search_ui.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets         = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.search_ui_tg.arn
    container_name   = "search-ui"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.http, aws_lb_target_group.search_ui_tg, aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
