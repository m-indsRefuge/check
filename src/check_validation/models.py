from dataclasses import dataclass
from typing import Final

CONTRACT_VERSION: Final[str] = "1.0"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    code: str
    path: str
    message: str
