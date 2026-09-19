# 🔐 AWS IAM Access Reviewer

<div align="center">

### Read-only AWS IAM security hygiene scanner for DevOps, Cloud & Security teams

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-IAM-FF9900?logo=amazonaws&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-automation-EE0000?logo=ansible&logoColor=white)

**Turn AWS IAM metadata into actionable security findings — without automatically changing production access.**

</div>

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Why This Project](#-why-this-project)
- [What It Checks](#-what-it-checks)
- [Key Features](#-key-features)
- [Architecture](#️-architecture)
- [How It Works](#-how-it-works)
- [Risk Model](#-risk-model)
- [Example Finding](#-example-finding)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Docker](#-docker)
- [Docker Compose](#-docker-compose)
- [AWS Permissions](#-aws-permissions)
- [Terraform](#-terraform)
- [Ansible](#-ansible)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [Security](#-security)
- [Multi-Account Design](#-multi-account-design)
- [Project Structure](#-project-structure)
- [Limitations](#️-limitations)
- [Roadmap](#️-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Overview

**AWS IAM Access Reviewer** is a production-oriented, read-only security tool that inspects AWS IAM user metadata and converts common identity hygiene problems into structured findings.

Instead of manually opening IAM pages and checking users one by one, the service collects identity information through AWS APIs, evaluates it against configurable rules, assigns severity and risk scores, and exposes the results through a simple FastAPI endpoint.

### The core idea

> **Discover → Analyze → Prioritize → Report → Remediate through an approved process**

The application is intentionally **read-only**. It reports what should be reviewed but does not automatically disable users, deactivate credentials, or delete IAM resources.

---

## 🎯 Why This Project?

IAM is one of the most important security boundaries in AWS.

Over time, environments can accumulate:

- Old access keys
- Unused active credentials
- Excessive administrator permissions
- Console-enabled users without MFA evidence
- Inline policies that are harder to centrally review
- Long-lived identities that should be replaced with temporary role-based access

These issues are easy to miss during normal DevOps operations.

This project provides a repeatable way to perform a basic IAM hygiene review and generate machine-readable findings that can later feed into dashboards, ticketing systems, SIEM pipelines, or security workflows.

---

## 🔍 What It Checks

| Check | Description | Default Severity |
|---|---|---|
| 🔴 Administrator access | Detects users with the AWS managed AdministratorAccess policy | Critical |
| 🔴 Stale access key | Detects active keys older than the configured threshold | High/Critical |
| 🟠 Unused active key | Detects active keys with no recent usage evidence | High |
| 🟠 Console without MFA | Flags console-capable users when MFA evidence is explicitly false | High |
| 🟡 Inline policies | Identifies users with inline IAM policies | Medium |

### Important

This is an **IAM hygiene scanner**, not a complete AWS permissions analyzer.

It does not currently calculate every effective permission inherited through:

- IAM groups
- Role assumption
- Permission boundaries
- Service Control Policies
- Resource-based policies
- AWS IAM Identity Center
- Session policies
- Other cross-account permission paths

---

## ✨ Key Features

### 🔐 Read-only security model

The scanner only collects IAM metadata and produces findings.

No automatic remediation is performed.

### ⚡ FastAPI service

Simple REST endpoints make the scanner easy to run locally, inside Docker, or as a cloud workload.

### ☁️ Native AWS integration

Uses the standard boto3 credential provider chain, so the application can work with:

- IAM roles
- EC2 instance profiles
- ECS task roles
- Environment credentials
- AWS CLI profiles
- Other supported boto3 credential sources

### 📊 Risk scoring

Every finding receives:

- Finding type
- Severity
- Numeric score
- Evidence
- Recommended action

### 🐳 Container ready

The Docker image:

- Uses Python 3.12 slim
- Runs as a non-root application user
- Does not contain test files
- Exposes port 8080

### 🏗️ Infrastructure as Code

Terraform provides a starting point for deploying a dedicated read-only reviewer role.

### ⚙️ Configuration management

Ansible can prepare a Docker host for running the service.

### 🧪 Automated testing

Pytest covers the analyzer and API health endpoint.

### 🛡️ CI security checks

GitHub Actions runs:

- Python tests
- Terraform validation
- Container build
- Trivy filesystem/security scanning

---

# 🏗️ Architecture

The high-level data flow:

~~~mermaid
flowchart LR
    U[Engineer / Security Team] --> API[FastAPI API]
    API --> C[AWS IAM Collector]
    C --> IAM[(AWS IAM)]
    C --> STS[AWS STS]
    C --> A[Rule Analyzer]
    A --> R[Risk Findings]
    R --> JSON[JSON API Response]
    R --> SIEM[Future SIEM / Ticketing]
~~~

### Application layers

~~~mermaid
flowchart TB
    subgraph Application
        API[FastAPI]
        Config[Configuration]
        Collector[AWS Collector]
        Analyzer[Security Analyzer]
        Models[Pydantic Models]
    end

    API --> Config
    API --> Collector
    Collector --> Analyzer
    Analyzer --> Models
    Models --> API
    Collector --> IAM[(AWS IAM)]
    Collector --> STS[AWS STS]
~~~

---

# 🔄 How It Works

The scanner follows a simple pipeline:

~~~mermaid
flowchart LR
    A[Start Review] --> B[Authenticate with AWS]
    B --> C[Identify AWS Account]
    C --> D[List IAM Users]
    D --> E[Collect Policies]
    E --> F[Inspect Access Keys]
    F --> G[Collect Last-Used Metadata]
    G --> H[Analyze Security Rules]
    H --> I[Calculate Severity]
    I --> J[Generate Findings]
    J --> K[Return JSON]
~~~

### Step 1 — Authenticate

The application uses boto3's standard AWS credential chain.

### Step 2 — Identify the account

AWS STS is used to determine the AWS account associated with the current credentials.

### Step 3 — Collect IAM metadata

For each IAM user, the collector gathers:

- Username
- ARN
- Attached policies
- Access-key metadata
- Key status
- Key creation date
- Last-used metadata
- Inline policy count
- Console access evidence

### Step 4 — Analyze

The analyzer applies deterministic rules to the collected metadata.

### Step 5 — Prioritize

Each finding receives a severity and score.

### Step 6 — Report

Results are returned through the API as structured JSON.

---

# 📊 Risk Model

The project uses a simple deterministic scoring model.

| Score | Severity | Meaning |
|---:|---|---|
| 0–3 | Low | Lower-priority hygiene issue |
| 4–6 | Medium | Review recommended |
| 7–8 | High | Security review should be prioritized |
| 9–10 | Critical | Significant privilege or credential concern |

### Examples

~~~text
Administrator access
Score: 10
Severity: Critical
~~~

~~~text
Active access key unused for 120 days
Score: 8
Severity: High
~~~

~~~text
Inline policy
Score: 5
Severity: Medium
~~~

The scoring system is intentionally transparent so teams can modify the rules for their own security standards.

---

# 🔎 Example Finding

A typical result:

~~~json
{
  "account": "123456789012",
  "principal": "deploy-user",
  "finding_type": "stale_access_key",
  "severity": "high",
  "score": 8,
  "evidence": "Access key age is 120 days.",
  "recommendation": "Rotate or remove the key; prefer short-lived IAM roles."
}
~~~

This format is useful because results can be consumed by:

- Security dashboards
- SIEM systems
- Ticketing systems
- Lambda workflows
- ChatOps
- Custom automation
- Compliance reports

---

# 🧰 Prerequisites

For local development:

- Python 3.12+
- AWS CLI configured
- AWS credentials with read-only IAM access
- Git

Optional:

- Docker
- Docker Compose
- Terraform 1.6+
- Ansible

---

# ⚡ Quick Start

## 1. Clone the repository

~~~bash
git clone https://github.com/RahulSinha9/aws-iam-access-reviewer.git
cd aws-iam-access-reviewer
~~~

## 2. Create a virtual environment

~~~bash
python3 -m venv .venv
source .venv/bin/activate
~~~

Windows:

~~~powershell
.venv\Scripts\activate
~~~

## 3. Install dependencies

~~~bash
pip install -r requirements.txt
~~~

## 4. Configure AWS credentials

For example:

~~~bash
aws configure
~~~

Verify:

~~~bash
aws sts get-caller-identity
~~~

## 5. Run tests

~~~bash
python -m pytest
~~~

## 6. Start the API

~~~bash
uvicorn app.main:app --reload --port 8080
~~~

## 7. Run a review

~~~bash
curl http://localhost:8080/api/v1/review
~~~

---

# 🐳 Docker

Build:

~~~bash
docker build -t aws-iam-access-reviewer .
~~~

Run:

~~~bash
docker run --rm \
  -p 8080:8080 \
  -e AWS_REGION=ap-south-1 \
  -v "$HOME/.aws:/home/app/.aws:ro" \
  aws-iam-access-reviewer
~~~

Then:

~~~bash
curl http://localhost:8080/api/v1/review
~~~

### Container security

The image runs as a dedicated non-root user, reducing the impact of an application-level compromise.

---

# 🐳 Docker Compose

Start:

~~~bash
docker compose up --build
~~~

Health check:

~~~bash
curl http://localhost:8080/health
~~~

Review:

~~~bash
curl http://localhost:8080/api/v1/review
~~~

---

# 🔐 AWS Permissions

The scanner should use a **dedicated read-only identity**.

The principle should be:

> Give the scanner only the AWS API permissions required to inspect IAM metadata.

The Terraform example provides a starting point using IAM read/list permissions and STS caller identity.

### Production recommendation

Do not use a personal administrator credential to run this application.

Prefer:

~~~text
Security/Audit Account
        |
        | AssumeRole
        v
Target AWS Account
        |
        v
Read-only IAM Reviewer Role
        |
        v
AWS IAM APIs
~~~

---

# 🏗️ Terraform

The terraform directory provides an infrastructure-as-code starting point for the reviewer role.

Initialize:

~~~bash
cd terraform
terraform init
~~~

Format:

~~~bash
terraform fmt -check
~~~

Validate:

~~~bash
terraform validate
~~~

Review:

~~~bash
terraform plan
~~~

### ⚠️ Before production

Review and narrow the trust relationship and IAM policy according to your deployment architecture.

The provided Terraform configuration is a starting point rather than a complete enterprise IAM governance module.

---

# ⚙️ Ansible

Ansible can prepare a Linux host for the application.

Example inventory:

~~~ini
[reviewer]
reviewer-01 ansible_host=10.0.10.20

[reviewer:vars]
ansible_user=ubuntu
~~~

Run:

~~~bash
ansible-playbook \
  -i ansible/inventory.example.ini \
  ansible/site.yml
~~~

The playbook:

1. Installs Docker
2. Enables Docker
3. Starts Docker
4. Creates the application directory

---

# 🌐 API Reference

## GET /health

Basic application health endpoint.

~~~bash
curl http://localhost:8080/health
~~~

Response:

~~~json
{
  "status": "ok"
}
~~~

## GET /api/v1/review

Runs the IAM review.

~~~bash
curl http://localhost:8080/api/v1/review
~~~

Example response structure:

~~~json
{
  "scanned_principals": 12,
  "findings": [
    {
      "account": "123456789012",
      "principal": "deploy-user",
      "finding_type": "unused_active_key",
      "severity": "high",
      "score": 8,
      "evidence": "Active access key has not been used for 120 days.",
      "recommendation": "Disable/remove the unused key after validating dependencies."
    }
  ],
  "risk_score": 8,
  "generated_at": "2026-09-19T00:00:00+00:00"
}
~~~

---

# 🧪 Testing

Run:

~~~bash
python -m pytest
~~~

The tests cover:

- Administrator finding detection
- Stale access-key detection
- Unused active-key detection
- Empty-risk summary behavior
- API health endpoint

### Test philosophy

The security rules are deterministic and unit-testable.

This makes it easier to extend the scanner with additional controls without coupling every rule to live AWS infrastructure.

---

# 🔄 CI/CD

GitHub Actions is configured under:

~~~text
.github/workflows/ci.yml
~~~

Pipeline:

~~~mermaid
flowchart LR
    Push[Git Push / Pull Request] --> Test[Python Tests]
    Push --> TF[Terraform Validate]
    Push --> Build[Container Build]
    Push --> Scan[Trivy Security Scan]
    Test --> Gate{Checks Pass?}
    TF --> Gate
    Build --> Gate
    Scan --> Gate
    Gate -->|Yes| Ready[Ready for Review]
    Gate -->|No| Fix[Fix Issues]
~~~

### CI stages

**🧪 Python**

Installs dependencies and runs Pytest.

**🏗️ Terraform**

Runs formatting and validation checks.

**🐳 Container**

Builds the Docker image to verify the container definition.

**🛡️ Trivy**

Scans the repository for vulnerabilities, secrets, and IaC misconfigurations.

The CI pipeline does not perform AWS mutation.

---

# 🛡️ Security

Security is a core design goal.

### Credential handling

Never commit:

~~~text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
.env
*.pem
~~~

Prefer:

- IAM roles
- Workload identity
- AWS profiles
- Short-lived credentials
- Secret managers

### Read-only by design

The scanner reports issues but does not automatically remediate them.

### Least privilege

The application's AWS identity should have only the API permissions required for the review.

### Auditability

For production environments, enable and retain CloudTrail logs and centralize security/audit events according to your organization's requirements.

---

# 🌍 Multi-Account Design

A useful enterprise pattern is to run the scanner from a central security account.

~~~mermaid
flowchart TB
    Security[Central Security Account]
    Reviewer[IAM Access Reviewer]

    Security --> Reviewer
    Reviewer --> R1[Assume Role]
    Reviewer --> R2[Assume Role]
    Reviewer --> R3[Assume Role]

    R1 --> A1[Production Account]
    R2 --> A2[Staging Account]
    R3 --> A3[Development Account]

    A1 --> IAM1[IAM Metadata]
    A2 --> IAM2[IAM Metadata]
    A3 --> IAM3[IAM Metadata]
~~~

This pattern can be extended so one reviewer service periodically scans multiple AWS accounts and produces a consolidated security report.

---

# 📁 Project Structure

~~~text
aws-iam-access-reviewer/
│
├── app/
│   ├── __init__.py
│   ├── analyzer.py          # IAM security rules and risk scoring
│   ├── aws.py               # AWS IAM/STS collector
│   ├── config.py            # Environment configuration
│   ├── main.py              # FastAPI application
│   └── models.py            # Finding data models
│
├── tests/
│   ├── test_analyzer.py     # Analyzer tests
│   └── test_api.py          # API tests
│
├── terraform/
│   ├── versions.tf          # Terraform/provider configuration
│   ├── iam.tf               # Reviewer IAM role/policy
│   └── outputs.tf           # Terraform outputs
│
├── ansible/
│   ├── site.yml             # Docker host preparation
│   └── inventory.example.ini
│
├── scripts/
│   └── review.sh            # Convenience review command
│
├── .github/
│   └── workflows/
│       └── ci.yml           # CI/security pipeline
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── Makefile
├── requirements.txt
├── pyproject.toml
└── README.md
~~~

---

# ⚠️ Limitations

This project intentionally starts with a focused scope.

### Current limitations

- IAM users are the primary reviewed identity type.
- MFA evidence is not yet collected directly from IAM MFA-device APIs.
- Administrator detection currently focuses on directly attached AdministratorAccess.
- Group-derived permissions are not fully resolved.
- IAM roles are not comprehensively analyzed.
- AWS IAM Identity Center is not currently analyzed.
- SCP evaluation is outside the current rule engine.
- Resource-based policies are not evaluated.
- Effective permission calculation is not performed.
- Findings are reported but not automatically remediated.

These limitations are documented intentionally so the scanner's output is not mistaken for a complete AWS IAM compliance assessment.

---

# 🗺️ Roadmap

### Phase 1 — IAM coverage

- [ ] Direct MFA device inspection
- [ ] IAM group analysis
- [ ] Role analysis
- [ ] Permission boundary detection
- [ ] More access-key usage analysis

### Phase 2 — Advanced AWS security

- [ ] IAM Access Analyzer integration
- [ ] AWS Organizations integration
- [ ] SCP visibility
- [ ] Cross-account trust analysis
- [ ] Resource-policy analysis

### Phase 3 — Security operations

- [ ] HTML security reports
- [ ] Prometheus metrics
- [ ] Grafana dashboard
- [ ] Slack/Teams notifications
- [ ] Jira ticket creation
- [ ] SIEM integration

### Phase 4 — Enterprise platform

- [ ] Multi-account scanning
- [ ] Scheduled scans
- [ ] Historical findings
- [ ] Finding deduplication
- [ ] Risk trend dashboards
- [ ] Approval-based remediation workflows

---

# 🤝 Contributing

Contributions are welcome.

Create a feature branch:

~~~bash
git checkout -b feature/my-improvement
~~~

Make changes and add tests.

Run:

~~~bash
python -m pytest
~~~

Commit:

~~~bash
git add .
git commit -m "feat: improve IAM analysis"
~~~

Push:

~~~bash
git push origin feature/my-improvement
~~~

Open a pull request and describe:

- What changed
- Why it changed
- How it was tested
- Any security implications

---

# 📜 License

This repository does not currently include a license file.

If you plan to publish the project as open source, add an appropriate license such as MIT, Apache-2.0, or another license that matches your intended usage.

---

# ⭐ DevOps Portfolio Value

This project demonstrates several real-world DevOps and cloud engineering concepts in one system:

~~~text
AWS IAM
   │
   ├── Security analysis
   ├── Least privilege
   ├── Access-key hygiene
   └── IAM roles
          │
          ▼
       Python
          │
          ├── FastAPI
          ├── boto3
          ├── Pydantic
          └── Pytest
          │
          ▼
       Docker
          │
          ▼
      Terraform
          │
          ▼
       Ansible
          │
          ▼
     GitHub Actions
          │
          ▼
      Trivy Scan
~~~

It demonstrates **AWS + Python + Security + Docker + Terraform + Ansible + CI/CD** rather than being only a small scripting exercise.

---

<div align="center">

### 🔐 Review access. Reduce risk. Keep AWS permissions intentional.

**Built as a practical DevOps / Cloud Security engineering project.**

</div>
