from ecommerce_agent.tools import search_products

for query in ["Blue Cotton Shirt", "Electronics", "Wireless Headphones"]:
    print(f"\nSearching: {query}")
    print(search_products(query))