from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerResponse


router = APIRouter(
    prefix="/customers",
    tags=["Customers"]
)


@router.get("/{customer_code}", response_model=CustomerResponse)
def get_customer(
    customer_code: str,
    db: Session = Depends(get_db)
):
    customer = (
        db.query(Customer)
        .filter(Customer.customer_code == customer_code)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer

@router.get("/", response_model=list[CustomerResponse])
def search_customers(
    name: str | None = None,
    db: Session = Depends(get_db)
):
    query = db.query(Customer)

    if name:
        query = query.filter(
            Customer.name.ilike(f"%{name}%")
        )

    return query.all()