data "aws_caller_identity" "current" {}

resource "aws_iam_role" "reviewer" {
  name = "aws-iam-access-reviewer"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "read_only_iam" {
  role = aws_iam_role.reviewer.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["iam:Get*", "iam:List*", "sts:GetCallerIdentity"]
      Resource = "*"
    }]
  })
}

output "reviewer_role_arn" {
  value = aws_iam_role.reviewer.arn
}
