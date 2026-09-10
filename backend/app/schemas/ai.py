from pydantic import BaseModel, Field


class NaturalLanguageQuoteRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )


class ParsedQuoteRequest(BaseModel):
    customer_name: str | None = None
    product_name: str | None = None
    quantity: int | None = None