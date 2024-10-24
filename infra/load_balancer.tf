# Load Balancer Configuration

resource "aws_lb" "alb" {
  name               = "ecs-alb"
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  security_groups    = [aws_security_group.ecs_sg.id]
}

# Target Groups

# Uncomment and configure the following target groups if needed
# resource "aws_lb_target_group" "fastapi_tg" {
#   name        = "fastapi-tg"
#   port        = 80
#   protocol    = "HTTP"
#   vpc_id      = aws_vpc.main.id
#   target_type = "ip"
# }

# resource "aws_lb_target_group" "fastapi_tg_2" {
#   name        = "fastapi-tg-2"
#   port        = 8000
#   protocol    = "HTTP"
#   vpc_id      = aws_vpc.main.id
#   target_type = "ip"
# }

resource "aws_lb_target_group" "search_ui_tg" {
  name        = "search-ui-tg"
  port        = 3000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

resource "aws_lb_target_group" "qdrant_tg" {
  name        = "qdrant-tg"
  port        = 6333
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
}

resource "aws_lb_target_group" "meilisearch_tg" {
  name        = "meilisearch-tg"
  port        = 7700
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
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
