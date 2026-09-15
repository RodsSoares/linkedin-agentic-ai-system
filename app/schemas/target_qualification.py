from typing import Literal

from pydantic import BaseModel


TargetType = Literal[
    "INTERACTION_TARGET",
    "LINKEDIN_CONTENT",
    "LINKEDIN_NON_INTERACTION",
    "EXTERNAL_CONTENT",
    "UNKNOWN",
]


class TargetQualification(BaseModel):
    target_type: TargetType
    is_interaction_target: bool
    reason: str
    