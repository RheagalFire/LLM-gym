# VPC 
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags       = { Name = "main-vpc" }
}

# Internet Gateway
resource "aws_internet_gateway" "gw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "main-gw" }
}

# Subnet for availability zone 1
resource "aws_subnet" "public_1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidr_1
  availability_zone = var.availability_zone
  tags              = { Name = "public-subnet" }
}

# Subnet for availability zone 2
resource "aws_subnet" "public_2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidr_2
  availability_zone = var.availability_zone_2
  tags              = { Name = "public-subnet-2" }
}

# Route Table
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.gw.id
  }
  tags = { Name = "public-route-table" }
}

# Route Table Association for availability zone 1
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public.id
}

# Route Table Association for availability zone 2
resource "aws_route_table_association" "public_2" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public.id
}
