# Create a resource for ECS cluster
resource "aws_ecs_cluster" "main" {
  name = "main-cluster"
}