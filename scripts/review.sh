#!/usr/bin/env bash
set -euo pipefail
curl --fail --silent --show-error http://localhost:8080/api/v1/review | python -m json.tool
