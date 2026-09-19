# AWS IAM Access Reviewer

A production-oriented, read-only AWS IAM hygiene scanner that turns identity metadata into prioritized security findings.

## Findings

- Administrator-level access
- Stale access keys
- Unused active access keys
- Console access without MFA evidence
- Inline policies

The tool reports evidence and recommendations. It does not automatically disable users or delete credentials.

## Architecture

AWS IAM -> Collector -> Analyzer -> Risk Findings -> JSON/API

## Local development

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload --port 8080

Then:

curl http://localhost:8080/api/v1/review

Use the standard AWS credential chain. Never commit credentials.

## Docker

docker build -t aws-iam-access-reviewer .
docker run --rm -p 8080:8080 \
  -e AWS_REGION=ap-south-1 \
  -v "$HOME/.aws:/home/app/.aws:ro" \
  aws-iam-access-reviewer

## Terraform

The terraform directory creates a read-only IAM reviewer role suitable as a starting point for workload identity.

cd terraform
terraform init
terraform fmt -check
terraform validate
terraform plan

Review the trust relationship and narrow the policy further for your actual deployment before production use.

## Ansible

ansible-playbook -i ansible/inventory.example.ini ansible/site.yml

## CI/CD

GitHub Actions runs Python tests, Terraform validation, container build, and Trivy vulnerability/secret/IaC scanning.

No CI job performs AWS mutation.

## Production security

- Prefer IAM roles/workload identity over static credentials.
- Scope IAM permissions to required read APIs.
- Enable CloudTrail and centralized audit logging.
- Store reports securely.
- Alert on critical findings.
- Use an approval workflow before remediation.
- For multi-account use, assume a dedicated read-only role from a security/audit account.

## Limitations

This initial version focuses on IAM users and common access-key hygiene. Complete IAM governance also requires analysis of Identity Center, groups, roles, permission boundaries, SCPs, resource policies, service-linked roles, and effective permissions.

## Project structure

aws-iam-access-reviewer/
├── app/
│   ├── analyzer.py
│   ├── aws.py
│   ├── config.py
│   ├── main.py
│   └── models.py
├── tests/
├── terraform/
├── ansible/
├── scripts/
├── .github/workflows/ci.yml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── README.md
