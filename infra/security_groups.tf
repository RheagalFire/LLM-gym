resource "aws_security_group" "ecs_sg" {
  name        = "ecs-security-group"
  description = "Allow necessary traffic"
  vpc_id      = aws_vpc.main.id

  # Inbound Rules
  ingress {
    description = "Allow HTTP"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to the world
  }
  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Open to the world
  }

  ingress {
    description = "Allow Meilisearch Port"
    from_port   = 7700
    to_port     = 7700
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Qdrant Port"
    from_port   = 6333
    to_port     = 6333
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow all traffic within the security group (inter-service communication)
  ingress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"  # All protocols
    self            = true
    cidr_blocks     = []
    ipv6_cidr_blocks = []
  }

  # Outbound Rules
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"  # All protocols
    cidr_blocks = ["0.0.0.0/0"]  # Allow all outbound traffic
  }

  tags = {
    Name = "ecs-sg"
  }
}
