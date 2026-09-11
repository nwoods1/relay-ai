from sqlalchemy.orm import Session

from app.tools.customer_tools import (
    create_customer_lookup_tool,
)
from app.tools.product_tools import (
    create_product_lookup_tool,
)
from app.tools.inventory_tools import (
    create_inventory_lookup_tool,
)
from app.tools.pricing_tools import (
    create_pricing_lookup_tool,
)
from app.tools.quote_tools import (
    create_quote_tool,
)


def create_business_tools(
    db: Session,
):
    return [
        create_customer_lookup_tool(db),
        create_product_lookup_tool(db),
        create_inventory_lookup_tool(db),
        create_pricing_lookup_tool(db),
        create_quote_tool(db),
    ]