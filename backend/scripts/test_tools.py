# from app.core.database import SessionLocal
# from app.tools.customer_tools import (
#     create_customer_lookup_tool,
# )
# from app.tools.product_tools import (
#     create_product_lookup_tool,
# )
# from app.tools.inventory_tools import (
#     create_inventory_lookup_tool,
# )
# from app.tools.pricing_tools import (
#     create_pricing_lookup_tool,
# )
# from app.tools.quote_tools import (
#     create_quote_tool,
# )

# def test_tools():
#     db = SessionLocal()

#     try:
#         customer_tool = create_customer_lookup_tool(
#             db
#         )
#         product_tool = create_product_lookup_tool(
#             db
#         )
#         inventory_tool = (
#             create_inventory_lookup_tool(db)
#         )
#         pricing_tool = (
#             create_pricing_lookup_tool(db)
#         )
#         quote_tool = create_quote_tool(db)



#         result = customer_tool.invoke(
#             {
#                 "customer_name": (
#                     "Pacific Mountain Outfitters"
#                 )
#             }
#         )

#         product_result = product_tool.invoke(
#             {
#                 "product_name": "Alpine Shell Jacket"
#             }
#         )

#         inventory_result = inventory_tool.invoke(
#             {
#                 "sku": "JACKET-BETA-AR-M"
#             }
#         )

#         pricing_result = pricing_tool.invoke(
#             {
#                 "customer_code": "BP-20001",
#                 "sku": "JACKET-BETA-AR-M",
#             }
#         )

#         quote_result = quote_tool.invoke(
#             {
#                 "customer_code": "BP-20001",
#                 "sku": "JACKET-BETA-AR-M",
#                 "quantity": 30,
#             }
#         )

#         print(result)
#         print(product_result)
#         print(inventory_result)
#         print(pricing_result)
#         print(quote_result)
    

#     finally:
#         db.close()


# if __name__ == "__main__":
#     test_tools()
from app.core.database import SessionLocal
from app.tools.registry import (
    create_business_tools,
)


def test_tools():
    db = SessionLocal()

    try:
        tools = create_business_tools(db)

        for business_tool in tools:
            print(
                business_tool.name,
                "-",
                business_tool.description,
            )

    finally:
        db.close()


if __name__ == "__main__":
    test_tools()