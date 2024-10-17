output "load_balancer_dns" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.alb.dns_name
}

output "ecs_cluster_id" {
  description = "The ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "ecs_service_fastapi" {
  description = "The ECS service for FastAPI app"
  value       = aws_ecs_service.fastapi_app.id
}

output "ecs_service_qdrant" {
  description = "The ECS service for Qdrant"
  value       = aws_ecs_service.qdrant.id
}

output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public_1.id
}

output "public_subnet_id_2" {
  description = "The ID of the public subnet"
  value       = aws_subnet.public_2.id
}
