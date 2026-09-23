












































































    







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