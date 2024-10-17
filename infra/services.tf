resource "aws_ecs_service" "fastapi_app" {
  name            = "fastapi-app-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.fastapi_app.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }
  # Add Load Balancer Mapping here
  load_balancer {
    target_group_arn = aws_lb_target_group.fastapi_tg_2.arn
    container_name   = "fastapi-app"
    container_port   = 8000
  }
  depends_on = [aws_lb_listener.http, aws_lb_target_group.fastapi_tg_2, aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
#
resource "aws_ecs_service" "qdrant" {
  name            = "qdrant-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.qdrant.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = [aws_subnet.public_1.id, aws_subnet.public_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  depends_on = [aws_iam_role_policy_attachment.ecs_task_execution_role_policy]
}
