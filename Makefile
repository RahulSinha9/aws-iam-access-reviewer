install:
	pip install -r requirements.txt

test:
	python -m pytest

run:
	uvicorn app.main:app --reload --port 8080

docker-build:
	docker build -t aws-iam-access-reviewer:local .

terraform-validate:
	cd terraform && terraform fmt -check && terraform init -backend=false && terraform validate
