from app.analyzer import analyze_principal, summarize

def test_admin_is_critical():
    findings = analyze_principal("123", {
        "name": "alice", "arn": "arn:aws:iam::123:user/alice",
        "has_admin_policy": True, "access_key_active": False,
        "console_access": False, "mfa_enabled": True, "inline_policy_count": 0
    })
    assert findings[0].finding_type == "administrator_access"
    assert findings[0].score == 10

def test_stale_and_unused_key():
    findings = analyze_principal("123", {
        "name": "bob", "arn": "arn:aws:iam::123:user/bob",
        "access_key_age_days": 120, "access_key_active": True,
        "unused_days": 120, "has_admin_policy": False,
        "console_access": False, "mfa_enabled": True, "inline_policy_count": 0
    })
    assert {f.finding_type for f in findings} == {"stale_access_key", "unused_active_key"}

def test_empty_summary():
    assert summarize([], 4)["risk_score"] == 0
