from decimal import Decimal

from app.core.database import SessionLocal
from app.models.customer import Customer
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.pricing import Pricing


def seed_database():
    db = SessionLocal()

    try:
        existing_customer = db.query(Customer).first()

        if existing_customer:
            print("Database already contains seed data.")
            return

        customers = [
            Customer(
                customer_code="BP-20001",
                name="Pacific Mountain Outfitters",
                region="BC",
                credit_status="approved",
                pricing_tier="B",
            ),
            Customer(
                customer_code="BP-20002",
                name="North Shore Outdoor Supply",
                region="BC",
                credit_status="approved",
                pricing_tier="A",
            ),
            Customer(
                customer_code="BP-20003",
                name="Rocky Mountain Adventure Co.",
                region="AB",
                credit_status="approved",
                pricing_tier="B",
            ),
            Customer(
                customer_code="BP-20004",
                name="Summit Trail Equipment",
                region="AB",
                credit_status="review",
                pricing_tier="C",
            ),
            Customer(
                customer_code="BP-20005",
                name="Northern Peak Outfitters",
                region="ON",
                credit_status="approved",
                pricing_tier="A",
            ),
        ]

        db.add_all(customers)

        warehouses = [
            Warehouse(
                code="VAN",
                name="Vancouver Distribution Centre",
                city="Vancouver",
                province="BC",
            ),
            Warehouse(
                code="CAL",
                name="Calgary Distribution Centre",
                city="Calgary",
                province="AB",
            ),
            Warehouse(
                code="TOR",
                name="Toronto Distribution Centre",
                city="Toronto",
                province="ON",
            ),
        ]

        db.add_all(warehouses)

        products = [
            Product(
                sku="JACKET-BETA-AR-M",
                name="Alpine Shell Jacket",
                category="Jackets",
                unit_size="Men's",
                base_price=Decimal("749.99"),
            ),
            Product(
                sku="JACKET-ATOM-W",
                name="Insulated Lightweight Jacket",
                category="Jackets",
                unit_size="Women's",
                base_price=Decimal("329.99"),
            ),
            Product(
                sku="PACK-ALPHA-35",
                name="Alpine 35L Backpack",
                category="Backpacks",
                unit_size="35L",
                base_price=Decimal("279.99"),
            ),
            Product(
                sku="PANTS-GAMMA-M",
                name="Technical Hiking Pants",
                category="Pants",
                unit_size="Men's",
                base_price=Decimal("199.99"),
            ),
            Product(
                sku="SHIRT-MERINO-W",
                name="Merino Wool Base Layer",
                category="Base Layers",
                unit_size="Women's",
                base_price=Decimal("129.99"),
            ),
            Product(
                sku="GLOVE-ALPINE",
                name="Waterproof Alpine Gloves",
                category="Accessories",
                unit_size="Unisex",
                base_price=Decimal("99.99"),
            ),
            Product(
                sku="TOQUE-MERINO",
                name="Merino Wool Toque",
                category="Accessories",
                unit_size="Unisex",
                base_price=Decimal("59.99"),
            ),
            Product(
                sku="PACK-TRAIL-20",
                name="Trail 20L Daypack",
                category="Backpacks",
                unit_size="20L",
                base_price=Decimal("179.99"),
            ),
        ]

        db.add_all(products)

        # This writes customers/products/warehouses so IDs are generated
        # before we create inventory and pricing rows.
        db.flush()

        warehouse_map = {
            warehouse.code: warehouse
            for warehouse in warehouses
        }

        product_map = {
            product.sku: product
            for product in products
        }

        inventory_rows = [
            Inventory(
                product_id=product_map["JACKET-BETA-AR-M"].id,
                warehouse_id=warehouse_map["VAN"].id,
                quantity_available=42,
                quantity_reserved=7,
            ),
            Inventory(
                product_id=product_map["JACKET-BETA-AR-M"].id,
                warehouse_id=warehouse_map["CAL"].id,
                quantity_available=28,
                quantity_reserved=4,
            ),
            Inventory(
                product_id=product_map["JACKET-BETA-AR-M"].id,
                warehouse_id=warehouse_map["TOR"].id,
                quantity_available=35,
                quantity_reserved=5,
            ),

            Inventory(
                product_id=product_map["JACKET-ATOM-W"].id,
                warehouse_id=warehouse_map["VAN"].id,
                quantity_available=65,
                quantity_reserved=12,
            ),
            Inventory(
                product_id=product_map["JACKET-ATOM-W"].id,
                warehouse_id=warehouse_map["CAL"].id,
                quantity_available=43,
                quantity_reserved=8,
            ),

            Inventory(
                product_id=product_map["PACK-ALPHA-35"].id,
                warehouse_id=warehouse_map["VAN"].id,
                quantity_available=31,
                quantity_reserved=3,
            ),
            Inventory(
                product_id=product_map["PACK-ALPHA-35"].id,
                warehouse_id=warehouse_map["TOR"].id,
                quantity_available=24,
                quantity_reserved=2,
            ),

            Inventory(
                product_id=product_map["PANTS-GAMMA-M"].id,
                warehouse_id=warehouse_map["CAL"].id,
                quantity_available=58,
                quantity_reserved=9,
            ),

            Inventory(
                product_id=product_map["SHIRT-MERINO-W"].id,
                warehouse_id=warehouse_map["VAN"].id,
                quantity_available=72,
                quantity_reserved=10,
            ),

            Inventory(
                product_id=product_map["GLOVE-ALPINE"].id,
                warehouse_id=warehouse_map["TOR"].id,
                quantity_available=86,
                quantity_reserved=11,
            ),

            Inventory(
                product_id=product_map["TOQUE-MERINO"].id,
                warehouse_id=warehouse_map["VAN"].id,
                quantity_available=120,
                quantity_reserved=15,
            ),

            Inventory(
                product_id=product_map["PACK-TRAIL-20"].id,
                warehouse_id=warehouse_map["CAL"].id,
                quantity_available=47,
                quantity_reserved=6,
            ),
        ]

        db.add_all(inventory_rows)

        pricing_rows = []

        pricing_data = {
            "JACKET-BETA-AR-M": {
                "A": "679.99",
                "B": "714.99",
                "C": "749.99",
            },
            "JACKET-ATOM-W": {
                "A": "299.99",
                "B": "314.99",
                "C": "329.99",
            },
            "PACK-ALPHA-35": {
                "A": "249.99",
                "B": "264.99",
                "C": "279.99",
            },
            "PANTS-GAMMA-M": {
                "A": "179.99",
                "B": "189.99",
                "C": "199.99",
            },
            "SHIRT-MERINO-W": {
                "A": "109.99",
                "B": "119.99",
                "C": "129.99",
            },
            "GLOVE-ALPINE": {
                "A": "84.99",
                "B": "92.99",
                "C": "99.99",
            },
            "TOQUE-MERINO": {
                "A": "49.99",
                "B": "54.99",
                "C": "59.99",
            },
            "PACK-TRAIL-20": {
                "A": "159.99",
                "B": "169.99",
                "C": "179.99",
            },
        }

        for sku, tiers in pricing_data.items():
            product = product_map[sku]

            for tier, price in tiers.items():
                pricing_rows.append(
                    Pricing(
                        product_id=product.id,
                        pricing_tier=tier,
                        unit_price=Decimal(price),
                    )
                )

        db.add_all(pricing_rows)

        db.commit()

        print("Seed data inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()