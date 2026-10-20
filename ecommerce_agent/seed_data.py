
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from ecommerce_agent.postgres_database import (
    engine,
    Category,
    Product,
    Inventory,
    Customer,
    Order,
    OrderItem,
)


CATEGORIES = [
    "Clothing",
    "Electronics",
    "Footwear",
    "Accessories",
]

PRODUCTS = [
    ("Blue Cotton Shirt", "Clothing", "1800.00", "Comfortable cotton shirt"),
    ("Black Jeans", "Clothing", "3200.00", "Classic slim-fit jeans"),
    ("White T-Shirt", "Clothing", "1200.00", "Everyday cotton T-shirt"),
    ("Denim Jacket", "Clothing", "4800.00", "Casual denim jacket"),
    ("Hoodie", "Clothing", "2800.00", "Warm fleece hoodie"),
    ("Wireless Headphones", "Electronics", "5500.00", "Bluetooth over-ear headphones"),
    ("Smart Watch", "Electronics", "8500.00", "Smart watch with fitness tracking"),
    ("USB-C Charger", "Electronics", "1800.00", "Fast charging USB-C adapter"),
    ("Bluetooth Speaker", "Electronics", "4200.00", "Portable wireless speaker"),
    ("Wireless Mouse", "Electronics", "2200.00", "Wireless computer mouse"),
    ("Running Shoes", "Footwear", "4500.00", "Lightweight running shoes"),
    ("Casual Sneakers", "Footwear", "3800.00", "Everyday casual sneakers"),
    ("Leather Sandals", "Footwear", "2500.00", "Comfortable leather sandals"),
    ("Sports Shoes", "Footwear", "5200.00", "Training and sports shoes"),
    ("Leather Wallet", "Accessories", "1200.00", "Compact leather wallet"),
    ("Travel Backpack", "Accessories", "3500.00", "Water-resistant travel backpack"),
    ("Sunglasses", "Accessories", "1600.00", "UV-protection sunglasses"),
    ("Wrist Watch", "Accessories", "6200.00", "Classic analog wrist watch"),
    ("Leather Belt", "Accessories", "1400.00", "Adjustable leather belt"),
    ("Laptop Sleeve", "Accessories", "1900.00", "Protective laptop sleeve"),
]

CUSTOMERS = [
    ("Ayesha Khan", "ayesha.khan@example.com"),
    ("Hamza Ali", "hamza.ali@example.com"),
    ("Fatima Ahmed", "fatima.ahmed@example.com"),
    ("Usman Malik", "usman.malik@example.com"),
    ("Zara Sheikh", "zara.sheikh@example.com"),
    ("Bilal Hussain", "bilal.hussain@example.com"),
    ("Hira Siddiqui", "hira.siddiqui@example.com"),
    ("Omar Farooq", "omar.farooq@example.com"),
    ("Maham Iqbal", "maham.iqbal@example.com"),
    ("Saad Qureshi", "saad.qureshi@example.com"),
]

# Customer index, order status, and (product index, quantity) pairs.
# Product indexes refer to the PRODUCTS list above.
ORDERS = [
    (0, "delivered", [(0, 2), (14, 1)]),
    (1, "shipped", [(5, 1), (9, 1)]),
    (2, "pending", [(10, 1), (2, 2)]),
    (3, "delivered", [(1, 1), (18, 1)]),
    (4, "processing", [(6, 1)]),
    (5, "shipped", [(15, 1), (7, 2)]),
    (6, "delivered", [(11, 1), (16, 1)]),
    (7, "pending", [(8, 1), (14, 2)]),
    (8, "processing", [(3, 1), (4, 1)]),
    (9, "delivered", [(17, 1)]),
    (0, "shipped", [(19, 1), (9, 1)]),
    (2, "pending", [(5, 1)]),
    (4, "delivered", [(12, 2)]),
    (6, "processing", [(13, 1), (18, 2)]),
    (8, "shipped", [(10, 1), (14, 1)]),
]


def seed_database():
    with Session(engine) as session:
        # Create categories if they do not already exist.
        category_map = {}

        for name in CATEGORIES:
            category = session.scalar(
                select(Category).where(Category.name == name)
            )

            if category is None:
                category = Category(name=name)
                session.add(category)

            category_map[name] = category

        session.flush()

        # Create products and inventory only if the seed products
        # are not already present.
        product_map = {}

        for name, category_name, price, description in PRODUCTS:
            product = session.scalar(
                select(Product).where(Product.name == name)
            )

            if product is None:
                product = Product(
                    name=name,
                    category=category_map[category_name],
                    price=Decimal(price),
                    description=description,
                )
                session.add(product)
                session.flush()

                session.add(
                    Inventory(
                        product=product,
                        stock_quantity=(
                            3 if name == "Wireless Headphones"
                            else 20
                        ),
                        reorder_level=5,
                    )
                )

            product_map[name] = product

        # Create fictional customers if their email is not present.
        customer_map = {}

        for name, email in CUSTOMERS:
            customer = session.scalar(
                select(Customer).where(Customer.email == email)
            )

            if customer is None:
                customer = Customer(name=name, email=email)
                session.add(customer)

            customer_map[email] = customer

        session.flush()

        # Add each seed order only once.
        for customer_index, status, items in ORDERS:
            customer_email = CUSTOMERS[customer_index][1]

            # Each customer has at most one seed order in this dataset,
            # except where noted. Use the unique seed marker in this
            # order's item combination to recognize existing orders.
            product_names = [
                PRODUCTS[product_index][0]
                for product_index, _ in items
            ]

            existing_order = None

            for order in customer_map[customer_email].orders:
                existing_names = {item.product.name for item in order.items}

                if existing_names == set(product_names):
                    existing_order = order
                    break

            if existing_order is not None:
                continue

            order = Order(
                customer=customer_map[customer_email],
                status=status,
                total_amount=Decimal("0.00"),
            )
            session.add(order)
            session.flush()

            total = Decimal("0.00")

            for product_index, quantity in items:
                product_name = PRODUCTS[product_index][0]
                product = product_map[product_name]
                unit_price = product.price

                session.add(
                    OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                )

                total += unit_price * quantity

            order.total_amount = total

        session.commit()

        print("Seed data inserted successfully.")
        print(f"Categories: {session.scalar(select(Category).count()) if False else len(CATEGORIES)}")
        print(f"Products in catalog: {session.scalar(select(Product).where(Product.id > 0).with_only_columns(Product.id).order_by(None).limit(1000).subquery().select()) if False else session.query(Product).count()}")
        print(f"Customers in database: {session.query(Customer).count()}")
        print(f"Orders in database: {session.query(Order).count()}")
        print(f"Order items in database: {session.query(OrderItem).count()}")


if __name__ == "__main__":
    try:
        seed_database()
    finally:
        engine.dispose()
