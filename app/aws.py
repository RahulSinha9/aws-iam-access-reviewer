from datetime import datetime, timezone
import boto3

def _days_since(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (datetime.now(timezone.utc) - dt).days)

def collect_iam_principals(region="ap-south-1"):
    iam = boto3.client("iam", region_name=region)
    sts = boto3.client("sts", region_name=region)
    account = sts.get_caller_identity()["Account"]
    principals = []
    for page in iam.get_paginator("list_users").paginate():
        for user in page.get("Users", []):
            name = user["UserName"]
            policies = iam.list_attached_user_policies(UserName=name)["AttachedPolicies"]
            keys = iam.list_access_keys(UserName=name)["AccessKeyMetadata"]
            active = [k for k in keys if k["Status"] == "Active"]
            age = _days_since(active[0]["CreateDate"]) if active else None
            unused = None
            if active:
                used = iam.get_access_key_last_used(AccessKeyId=active[0]["AccessKeyId"])
                unused = _days_since(used.get("AccessKeyLastUsed", {}).get("LastUsedDate"))
                if unused is None:
                    unused = 10**9
            principals.append({
                "name": name, "arn": user["Arn"],
                "access_key_age_days": age,
                "access_key_active": bool(active),
                "unused_days": unused,
                "has_admin_policy": any(p["PolicyArn"].endswith("AdministratorAccess") for p in policies),
                "mfa_enabled": None,
                "console_access": bool(user.get("PasswordLastUsed")),
                "inline_policy_count": len(iam.list_user_policies(UserName=name).get("PolicyNames", []))
            })
    return account, principals
