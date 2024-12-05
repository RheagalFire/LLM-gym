# Load Balancer Configuration

resource "aws_lb" "alb" {
  name               = "ecs-alb"
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  security_groups    = [aws_security_group.ecs_sg.id]
}

# Target Groups
resource "aws_lb_target_group" "search_ui_tg" {
  name        = "search-ui-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

# Qdrant Target Group
resource "aws_lb_target_group" "qdrant_tg" {
  name        = "qdrant-tg"
  port        = 6333
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

# Meilisearch Target Group
resource "aws_lb_target_group" "meilisearch_tg" {
  name        = "meilisearch-tg"
  port        = 7700
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

# Target Group for API Service
resource "aws_lb_target_group" "api_service_tg" {
  name        = "api-service-tg"
  port        = 8000  # Change this to the port your API service listens on
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"  # Assuming your API service is using IP targets
}

# Listeners

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.search_ui_tg.arn
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.search_ui_tg.arn
  }

  lifecycle {
    create_before_destroy = true
  }
}

// Add additional certificate using aws_lb_listener_certificate
resource "aws_lb_listener_certificate" "additional_cert" {
  listener_arn    = aws_lb_listener.https.arn
  certificate_arn = var.additional_certificate_arn
}

# Listener Rules
locals {
  listeners = {
    http  = aws_lb_listener.http.arn
    https = aws_lb_listener.https.arn
  }
}

resource "aws_lb_listener_rule" "qdrant_subdomain_rule" {
  for_each = local.listeners

  listener_arn = each.value

  priority = 100

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.qdrant_tg.arn
  }

  condition {
        host_header {
        values = [var.qdrant_host_header]
    }
  }
}

resource "aws_lb_listener_rule" "meilisearch_subdomain_rule" {
  for_each = local.listeners

  listener_arn = each.value
  priority = 200

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.meilisearch_tg.arn
  }

  condition {
    host_header {
      values = [var.meilisearch_host_header]
    }
  }
}

# Update Listener for Search UI to route to API Service
resource "aws_lb_listener_rule" "api_rule" {
  for_each = local.listeners

  listener_arn = each.value
  priority     = 300

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api_service_tg.arn
  }

  condition {
    host_header {
      values = [var.api_service_host_header]
    }
  }
}
