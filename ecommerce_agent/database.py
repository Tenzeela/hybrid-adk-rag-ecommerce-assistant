
import sqlite3
from pathlib import Path

# Store the database in the project's data folder
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / "ecommerce.db"


def create_database():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM products")
    product_count = cursor.fetchone()[0]

    if product_count == 0:
        products = [
            ("Blue Cotton Shirt", "Clothing", 1800.00, 25),
            ("Black Jeans", "Clothing", 3200.00, 12),
            ("Wireless Headphones", "Electronics", 5500.00, 8),
            ("Running Shoes", "Footwear", 4500.00, 15),
            ("Leather Wallet", "Accessories", 1200.00, 30),
        ]

        cursor.executemany("""
            INSERT INTO products (name, category, price, stock)
            VALUES (?, ?, ?, ?)
        """, products)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print(f"Database created successfully at: {DB_PATH}")
