
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from .postgres_database import (
    engine,
    Product,
    Inventory,
    Category,
    Customer,
    CustomerMemory,
)
from .rag import search_knowledge


# --------------------------------------------------
# 1. PRODUCT SEARCH — PostgreSQL
# --------------------------------------------------

def search_products(query: str) -> dict:
    """Search PostgreSQL for products by name or category."""

    if not query or not query.strip():
        return {
            "success": True,
            "message": "Please provide a product name or category.",
            "products": [],
        }

    try:
        search_term = f"%{query.strip()}%"

        with Session(engine) as session:
            statement = (
                select(Product, Inventory)
                .outerjoin(
                    Inventory,
                    Product.id == Inventory.product_id,
                )
                .where(
                    or_(
                        Product.name.ilike(search_term),
                        Product.category.has(
                            Category.name.ilike(search_term)
                        ),
                    )
                )
                .order_by(Product.name)
                .limit(10)
            )

            rows = session.execute(statement).all()
            products = []

            for product, inventory in rows:
                products.append({
                    "id": product.id,
                    "name": product.name,
                    "category": product.category.name,
                    "price": float(product.price),
                    "stock": (
                        inventory.stock_quantity
                        if inventory is not None
                        else 0
                    ),
                })

        if not products:
            return {
                "success": True,
                "message": f"No products found matching '{query}'.",
                "products": [],
            }

        message = "\n".join(
            f"Product: {p['name']}; "
            f"Category: {p['category']}; "
            f"Price: {p['price']:.2f}; "
            f"Stock: {p['stock']} units"
            for p in products
        )

        return {
            "success": True,
            "message": message,
            "products": products,
        }

    except Exception:
        return {
            "success": False,
            "message": "Unable to search the product catalog.",
            "products": [],
        }


# --------------------------------------------------
# 2. POLICY SEARCH — ChromaDB RAG
# --------------------------------------------------

def search_policies(query: str) -> dict:
    """Search store policy and knowledge documents using ChromaDB."""

    try:
        results = search_knowledge(query, n_results=2)

        if not results:
            return {
                "success": True,
                "message": "No relevant policy information was found.",
                "results": [],
            }

        return {
            "success": True,
            "results": [
                {
                    "source": result["source"],
                    "text": result["text"],
                }
                for result in results
            ],
        }

    except Exception:
        return {
            "success": False,
            "message": "Unable to search policy documents.",
            "results": [],
        }


# --------------------------------------------------
# 3. SAVE CUSTOMER MEMORY — PostgreSQL
# --------------------------------------------------

def save_customer_memory(
    customer_id: int,
    memory_type: str,
    memory_text: str,
) -> dict:
    """Save a useful memory for an existing customer."""

    if (
        not memory_type
        or not memory_type.strip()
        or not memory_text
        or not memory_text.strip()
    ):
        return {
            "success": False,
            "message": "Memory type and text are required.",
        }

    try:
        with Session(engine) as session:
            customer = session.get(Customer, customer_id)

            if customer is None:
                return {
                    "success": False,
                    "message": f"Customer {customer_id} was not found.",
                }

            memory = CustomerMemory(
                customer_id=customer_id,
                memory_type=memory_type.strip(),
                memory_text=memory_text.strip(),
            )

            session.add(memory)
            session.commit()

            return {
                "success": True,
                "message": "Customer memory saved.",
                "memory_id": memory.id,
            }

    except Exception:
        return {
            "success": False,
            "message": "Could not save customer memory.",
        }


# --------------------------------------------------
# 4. RETRIEVE CUSTOMER MEMORIES — PostgreSQL
# --------------------------------------------------

def get_customer_memories(customer_id: int) -> dict:
    """Retrieve saved memories for one existing customer."""

    try:
        with Session(engine) as session:
            customer = session.get(Customer, customer_id)

            if customer is None:
                return {
                    "success": False,
                    "message": f"Customer {customer_id} was not found.",
                    "memories": [],
                }

            statement = (
                select(CustomerMemory)
                .where(
                    CustomerMemory.customer_id == customer_id
                )
                .order_by(CustomerMemory.id.desc())
            )

            memories = session.scalars(statement).all()

            return {
                "success": True,
                "customer_id": customer_id,
                "customer_name": customer.name,
                "memories": [
                    {
                        "id": memory.id,
                        "type": memory.memory_type,
                        "text": memory.memory_text,
                    }
                    for memory in memories
                ],
            }

    except Exception:
        return {
            "success": False,
            "message": "Could not retrieve customer memories.",
            "memories": [],
        }


# --------------------------------------------------
# 5. CURRENT CUSTOMER — TEMPORARY DEMO CONFIGURATION
# --------------------------------------------------

# For local testing only.
# In production, derive the customer ID from authenticated
# user/session data instead of hardcoding it.
DEMO_CUSTOMER_ID = 1


def get_current_customer_memories() -> dict:
    """Retrieve memories for the current demo customer."""

    return get_customer_memories(DEMO_CUSTOMER_ID)


def remember_for_current_customer(
    memory_type: str,
    memory_text: str,
) -> dict:
    """Save a memory for the current demo customer."""

    return save_customer_memory(
        customer_id=DEMO_CUSTOMER_ID,
        
        memory_type=memory_type,
        memory_text=memory_text,
    )
