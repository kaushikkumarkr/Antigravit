
import os
import random
import time
from datetime import datetime, timedelta
from faker import Faker
import psycopg2
from psycopg2.extras import execute_values

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "analytics_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres_password")

# Seed Counts
NUM_CUSTOMERS = 500
NUM_PRODUCTS = 50
NUM_ORDERS = 5000
NUM_PAGE_VIEWS = 50000

fake = Faker()

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def seed_customers(cur):
    print(f"Seeding {NUM_CUSTOMERS} customers...")
    customers = []
    for _ in range(NUM_CUSTOMERS):
        created_at = fake.date_time_between(start_date='-2y', end_date='now')
        customer_type = random.choices(['free', 'pro', 'enterprise'], weights=[60, 30, 10])[0]
        customers.append((
            fake.name()[:50],
            fake.unique.email()[:50],
            customer_type,
            fake.job()[:50], # industry proxy
            created_at
        ))
    
    execute_values(cur, """
        INSERT INTO customers (name, email, customer_type, industry, created_at)
        VALUES %s
    """, customers)

def seed_products(cur):
    print(f"Seeding {NUM_PRODUCTS} products...")
    products = []
    categories = ['Electronics', 'Books', 'Home', 'Clothing', 'Software']
    
    for _ in range(NUM_PRODUCTS):
        price = round(random.uniform(10, 1000), 2)
        cost = round(price * random.uniform(0.4, 0.7), 2)
        products.append((
            fake.catch_phrase(),
            random.choice(categories),
            price,
            cost,
            random.randint(0, 1000),
            fake.date_time_between(start_date='-2y', end_date='now')
        ))

    execute_values(cur, """
        INSERT INTO products (name, category, price, cost, stock_quantity, created_at)
        VALUES %s
    """, products)

def seed_orders(cur):
    print(f"Seeding {NUM_ORDERS} orders and items...")
    pass # Replaced by seed_orders_safe logic

def seed_orders_safe(conn):
    print(f"Seeding {NUM_ORDERS} orders (slow safe mode)...")
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM customers")
    customer_ids = [r[0] for r in cur.fetchall()]
    
    cur.execute("SELECT id, price FROM products")
    product_map = {r[0]: r[1] for r in cur.fetchall()}
    product_ids = list(product_map.keys())
    
    batch_size = 100
    
    for i in range(0, NUM_ORDERS):
        customer_id = random.choice(customer_ids)
        created_at = fake.date_time_between(start_date='-1y', end_date='now')
        status = random.choices(['completed', 'pending', 'cancelled', 'refunded'], weights=[80, 10, 5, 5])[0]
        
        # Items
        num_items = random.randint(1, 5)
        current_ord_items = []
        total_amount = 0
        
        for _ in range(num_items):
            prod_id = random.choice(product_ids)
            qty = random.randint(1, 3)
            price = float(product_map[prod_id])
            total_amount += price * qty
            current_ord_items.append({'pid': prod_id, 'qty': qty, 'price': price})
            
        cur.execute("""
            INSERT INTO orders (customer_id, status, total_amount, created_at)
            VALUES (%s, %s, %s, %s) RETURNING id
        """, (customer_id, status, total_amount, created_at))
        order_id = cur.fetchone()[0]
        
        item_tuples = [(order_id, x['pid'], x['qty'], x['price']) for x in current_ord_items]
        execute_values(cur, """
            INSERT INTO order_items (order_id, product_id, quantity, unit_price)
            VALUES %s
        """, item_tuples)
        
        if i % 500 == 0:
            conn.commit()
            print(f"Generated {i} orders...")
            
    conn.commit()

def seed_page_views(cur):
    print(f"Seeding {NUM_PAGE_VIEWS} page views...")
    views = []
    pages = ['/home', '/pricing', '/products', '/blog', '/contact', '/dashboard']
    referrers = ['google.com', 'twitter.com', 'linkedin.com', 'direct']
    
    for _ in range(NUM_PAGE_VIEWS):
        views.append((
            fake.uuid4(),
            random.choice(pages),
            random.choice(referrers),
            fake.user_agent(),
            fake.date_time_between(start_date='-30d', end_date='now')
        ))
        
    execute_values(cur, """
        INSERT INTO page_views (session_id, page_url, referrer, user_agent, created_at)
        VALUES %s
    """, views)

def main():
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        print("Starting seed process...")
        seed_customers(cur)
        seed_products(cur)
        conn.commit()
        
        cur.close() 
        seed_orders_safe(conn) # Uses its own cursor and commits
        
        cur = conn.cursor()
        seed_page_views(cur)
        conn.commit()
        
        print("Seeding complete!")
        conn.close()
    except Exception as e:
        print(f"Error seeding data: {e}")

if __name__ == "__main__":
    main()
