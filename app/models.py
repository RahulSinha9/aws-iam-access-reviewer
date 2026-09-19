from typing import Literal
from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high", "critical"]

class AccessFinding(BaseModel):
    account: str
    principal: str
    finding_type: str
    severity: Severity
    score: int = Field(ge=0, le=10)
    evidence: str
    recommendation: str
