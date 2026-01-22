-- Antigravirt Database Schema
-- Version: 1.0

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Customers Table
CREATE TABLE customers (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    customer_type   VARCHAR(20) CHECK (customer_type IN ('free', 'pro', 'enterprise')),
    industry        VARCHAR(50),
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 2. Products Table
CREATE TABLE products (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        VARCHAR(50),
    price           DECIMAL(10,2) NOT NULL,
    cost            DECIMAL(10,2),
    stock_quantity  INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 3. Orders Table
CREATE TABLE orders (
    id              SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(id),
    status          VARCHAR(20) CHECK (status IN ('pending', 'completed', 'cancelled', 'refunded')),
    total_amount    DECIMAL(10,2) NOT NULL,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- 4. Order Items Table
CREATE TABLE order_items (
    id              SERIAL PRIMARY KEY,
    order_id        INTEGER REFERENCES orders(id),
    product_id      INTEGER REFERENCES products(id),
    quantity        INTEGER NOT NULL,
    unit_price      DECIMAL(10,2) NOT NULL
);

-- 5. Page Views Table
CREATE TABLE page_views (
    id              SERIAL PRIMARY KEY,
    session_id      VARCHAR(100),
    page_url        VARCHAR(500),
    referrer        VARCHAR(500),
    user_agent      TEXT,
    created_at      TIMESTAMP DEFAULT NOW()
);

-- Indexes for frequent query patterns
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_page_views_created_at ON page_views(created_at);
