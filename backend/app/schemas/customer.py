from pydantic import BaseModel, ConfigDict


class CustomerResponse(BaseModel):
    id: int
    customer_code: str
    name: str
    region: str
    credit_status: str
    pricing_tier: str

    model_config = ConfigDict(from_attributes=True)