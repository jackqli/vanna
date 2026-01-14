#!/usr/bin/env python
"""
Setup script to create tables and populate sample data in the SQLite database.
Run this script to initialize the database with sample data for testing.
"""

import os
import sqlite3
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_db_path():
    """Get the SQLite database path from environment or default"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    default_path = os.path.join(base_dir, 'data', 'database.db')
    db_path = os.getenv('SQLITE_DB_PATH', default_path)
    return os.path.abspath(db_path)

def create_tables(conn):
    """Create database tables"""
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    logger.info("Created table: users")

    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    logger.info("Created table: products")

    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    logger.info("Created table: orders")

    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    logger.info("Created table: order_items")

    conn.commit()

def insert_sample_data(conn):
    """Insert sample data into tables"""
    cursor = conn.cursor()

    # Check if data already exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        logger.info("Sample data already exists, skipping insert")
        return

    # Insert users
    users = [
        ('Alice Johnson', 'alice@example.com'),
        ('Bob Smith', 'bob@example.com'),
        ('Charlie Brown', 'charlie@example.com'),
        ('Diana Ross', 'diana@example.com'),
        ('Edward Chen', 'edward@example.com'),
        ('Fiona Williams', 'fiona@example.com'),
        ('George Miller', 'george@example.com'),
        ('Helen Davis', 'helen@example.com'),
        ('Ivan Petrov', 'ivan@example.com'),
        ('Julia Garcia', 'julia@example.com'),
    ]
    cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", users)
    logger.info(f"Inserted {len(users)} users")

    # Insert products
    products = [
        ('Laptop', 'High-performance laptop with 16GB RAM', 999.99, 50, 'Electronics'),
        ('Smartphone', 'Latest smartphone with 128GB storage', 699.99, 100, 'Electronics'),
        ('Headphones', 'Wireless noise-canceling headphones', 199.99, 200, 'Electronics'),
        ('Coffee Maker', 'Automatic drip coffee maker', 79.99, 75, 'Home & Kitchen'),
        ('Desk Chair', 'Ergonomic office chair', 299.99, 30, 'Furniture'),
        ('Running Shoes', 'Lightweight running shoes', 129.99, 150, 'Sports'),
        ('Backpack', 'Water-resistant travel backpack', 59.99, 200, 'Accessories'),
        ('Watch', 'Smart fitness watch', 249.99, 80, 'Electronics'),
        ('Keyboard', 'Mechanical gaming keyboard', 149.99, 120, 'Electronics'),
        ('Mouse', 'Wireless ergonomic mouse', 49.99, 180, 'Electronics'),
        ('Monitor', '27-inch 4K display', 449.99, 40, 'Electronics'),
        ('Tablet', '10-inch tablet with stylus', 399.99, 60, 'Electronics'),
        ('Camera', 'Digital mirrorless camera', 899.99, 25, 'Electronics'),
        ('Blender', 'High-speed blender', 89.99, 90, 'Home & Kitchen'),
        ('Yoga Mat', 'Non-slip exercise mat', 29.99, 250, 'Sports'),
    ]
    cursor.executemany(
        "INSERT INTO products (name, description, price, stock, category) VALUES (?, ?, ?, ?, ?)",
        products
    )
    logger.info(f"Inserted {len(products)} products")

    # Insert orders
    orders = [
        (1, 1199.98, 'completed'),
        (2, 699.99, 'completed'),
        (3, 329.98, 'shipped'),
        (1, 249.99, 'completed'),
        (4, 1349.98, 'processing'),
        (5, 179.98, 'completed'),
        (6, 999.99, 'shipped'),
        (7, 499.98, 'pending'),
        (8, 89.99, 'completed'),
        (9, 1299.98, 'completed'),
        (10, 279.98, 'processing'),
        (2, 449.99, 'shipped'),
        (3, 129.99, 'completed'),
        (4, 59.99, 'completed'),
        (5, 849.98, 'pending'),
    ]
    cursor.executemany(
        "INSERT INTO orders (user_id, total_amount, status) VALUES (?, ?, ?)",
        orders
    )
    logger.info(f"Inserted {len(orders)} orders")

    # Insert order items
    order_items = [
        (1, 1, 1, 999.99),   # Order 1: 1 Laptop
        (1, 3, 1, 199.99),   # Order 1: 1 Headphones
        (2, 2, 1, 699.99),   # Order 2: 1 Smartphone
        (3, 6, 1, 129.99),   # Order 3: 1 Running Shoes
        (3, 3, 1, 199.99),   # Order 3: 1 Headphones
        (4, 8, 1, 249.99),   # Order 4: 1 Watch
        (5, 1, 1, 999.99),   # Order 5: 1 Laptop
        (5, 9, 1, 149.99),   # Order 5: 1 Keyboard
        (5, 10, 4, 49.99),   # Order 5: 4 Mice
        (6, 6, 1, 129.99),   # Order 6: 1 Running Shoes
        (6, 10, 1, 49.99),   # Order 6: 1 Mouse
        (7, 1, 1, 999.99),   # Order 7: 1 Laptop
        (8, 11, 1, 449.99),  # Order 8: 1 Monitor
        (8, 10, 1, 49.99),   # Order 8: 1 Mouse
        (9, 14, 1, 89.99),   # Order 9: 1 Blender
        (10, 13, 1, 899.99), # Order 10: 1 Camera
        (10, 12, 1, 399.99), # Order 10: 1 Tablet
        (11, 8, 1, 249.99),  # Order 11: 1 Watch
        (11, 15, 1, 29.99),  # Order 11: 1 Yoga Mat
        (12, 11, 1, 449.99), # Order 12: 1 Monitor
        (13, 6, 1, 129.99),  # Order 13: 1 Running Shoes
        (14, 7, 1, 59.99),   # Order 14: 1 Backpack
        (15, 2, 1, 699.99),  # Order 15: 1 Smartphone
        (15, 9, 1, 149.99),  # Order 15: 1 Keyboard
    ]
    cursor.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
        order_items
    )
    logger.info(f"Inserted {len(order_items)} order items")

    conn.commit()

def print_summary(conn):
    """Print a summary of the database contents"""
    cursor = conn.cursor()

    print("\n" + "="*50)
    print("DATABASE SUMMARY")
    print("="*50)

    tables = ['users', 'products', 'orders', 'order_items']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count} records")

    print("\n" + "-"*50)
    print("SAMPLE QUERIES YOU CAN ASK:")
    print("-"*50)
    print("  - How many users are there?")
    print("  - What is the total revenue?")
    print("  - Show me all products in Electronics category")
    print("  - Which user has the most orders?")
    print("  - What are the top 5 most expensive products?")
    print("  - How many orders are pending?")
    print("  - What is the average order amount?")
    print("="*50 + "\n")

def main():
    """Main function to setup the database"""
    db_path = get_db_path()
    logger.info(f"Database path: {db_path}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to database
    logger.info("Connecting to SQLite database...")
    conn = sqlite3.connect(db_path)

    try:
        # Create tables
        logger.info("Creating tables...")
        create_tables(conn)

        # Insert sample data
        logger.info("Inserting sample data...")
        insert_sample_data(conn)

        # Print summary
        print_summary(conn)

        logger.info("Database setup completed successfully!")

    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    main()
