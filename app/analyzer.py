from datetime import datetime, timezone
from .models import AccessFinding

def severity(score: int) -> str:
    return "critical" if score >= 9 else "high" if score >= 7 else "medium" if score >= 4 else "low"

def analyze_principal(account: str, principal: dict, stale_days: int = 90):
    findings = []
    name = principal.get("name", principal["arn"])
    if principal.get("access_key_age_days") is not None and principal["access_key_age_days"] >= stale_days:
        score = 9 if principal["access_key_age_days"] >= stale_days * 2 else 8
        findings.append(AccessFinding(
            account=account, principal=name, finding_type="stale_access_key",
            severity=severity(score), score=score,
            evidence=f"Access key age is {principal['access_key_age_days']} days.",
            recommendation="Rotate or remove the key; prefer short-lived IAM roles."
        ))
    if principal.get("has_admin_policy"):
        findings.append(AccessFinding(
            account=account, principal=name, finding_type="administrator_access",
            severity="critical", score=10,
            evidence="Principal has an administrator-level policy.",
            recommendation="Replace broad administrator access with least-privilege permissions."
        ))
    if principal.get("access_key_active") and principal.get("unused_days", 0) >= stale_days:
        findings.append(AccessFinding(
            account=account, principal=name, finding_type="unused_active_key",
            severity="high", score=8,
            evidence=f"Active access key has not been used for {principal['unused_days']} days.",
            recommendation="Disable/remove the unused key after validating dependencies."
        ))
    if principal.get("mfa_enabled") is False and principal.get("console_access"):
        findings.append(AccessFinding(
            account=account, principal=name, finding_type="console_without_mfa",
            severity="high", score=8,
            evidence="Console-capable identity does not have MFA evidence.",
            recommendation="Require phishing-resistant MFA for interactive access."
        ))
    if principal.get("inline_policy_count", 0) > 0:
        findings.append(AccessFinding(
            account=account, principal=name, finding_type="inline_policy",
            severity="medium", score=5,
            evidence=f"Principal has {principal['inline_policy_count']} inline policies.",
            recommendation="Prefer managed, reviewable policies and remove unnecessary inline permissions."
        ))
    return findings

def summarize(findings, scanned):
    return {
        "scanned_principals": scanned,
        "findings": [f.model_dump() for f in findings],
        "risk_score": max((f.score for f in findings), default=0),
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
