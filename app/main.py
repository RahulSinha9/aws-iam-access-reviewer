from fastapi import FastAPI, HTTPException
from .config import get_settings
from .aws import collect_iam_principals
from .analyzer import analyze_principal, summarize

app = FastAPI(title="AWS IAM Access Reviewer", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/v1/review")
def review():
    settings = get_settings()
    try:
        account, principals = collect_iam_principals(settings.aws_region)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"AWS IAM collection failed: {exc}") from exc
    findings = []
    for principal in principals:
        findings.extend(analyze_principal(account, principal, settings.stale_days))
    return summarize(findings[:settings.max_findings], len(principals))
