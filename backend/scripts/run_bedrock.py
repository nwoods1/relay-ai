from app.llm.bedrock import parse_quote_request


result = parse_quote_request(
    "Can Pacific Mountain Outfitters get 30 Alpine Shell Jackets?"
)

print(result)