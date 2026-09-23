from pydantic import BaseModel


class GuardrailResult(BaseModel):
    allowed: bool

    reason: str | None = None

    category: str | None = None