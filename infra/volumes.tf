# Create EFS File System
resource "aws_efs_file_system" "qdrant_fs" {
  creation_token = "qdrant-efs"
  lifecycle_policy {
    transition_to_ia = "AFTER_14_DAYS"
  }
  encrypted = true
  tags = {
    Name = "qdrant-efs"
  }
}

resource "aws_efs_file_system" "meilisearch_fs" {
  creation_token = "meilisearch-efs"
  lifecycle_policy {
    transition_to_ia = "AFTER_14_DAYS"
  }
  encrypted = true
  tags = {
    Name = "meilisearch-efs"
  }
}

# Mount Targets for Qdrant EFS
resource "aws_efs_mount_target" "qdrant_mt_1" {
  file_system_id  = aws_efs_file_system.qdrant_fs.id
  subnet_id       = aws_subnet.public_1.id
  security_groups = [aws_security_group.efs_sg.id]
}

resource "aws_efs_mount_target" "qdrant_mt_2" {
  file_system_id  = aws_efs_file_system.qdrant_fs.id
  subnet_id       = aws_subnet.public_2.id
  security_groups = [aws_security_group.efs_sg.id]
}

# Mount Targets for Meilisearch EFS
resource "aws_efs_mount_target" "meilisearch_mt_1" {
  file_system_id  = aws_efs_file_system.meilisearch_fs.id
  subnet_id       = aws_subnet.public_1.id
  security_groups = [aws_security_group.efs_sg.id]
}

resource "aws_efs_mount_target" "meilisearch_mt_2" {
  file_system_id  = aws_efs_file_system.meilisearch_fs.id
  subnet_id       = aws_subnet.public_2.id
  security_groups = [aws_security_group.efs_sg.id]
}
