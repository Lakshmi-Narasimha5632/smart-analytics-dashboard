import pandas as pd
from db.connection import connect_db

conn = connect_db()
cursor = conn.cursor()

def fetch_data(query, columns):
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=columns)

    # convert numeric safely
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="ignore")

    return df

# ---------------- KPIs ---------------- #
def total_revenue():
    return fetch_data(
        "SELECT SUM(total_amount) FROM orders_1;",
        ["Total Revenue"]
    )

def avg_order_value():
    return fetch_data(
        "SELECT AVG(total_amount) FROM orders_1;",
        ["AOV"]
    )

# ---------------- REVENUE ---------------- #
def monthly_revenue():
    return fetch_data("""
        SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
               SUM(total_amount) AS revenue
        FROM orders_1
        GROUP BY month
        ORDER BY month;
    """, ["Month", "Revenue"])

def daily_revenue():
    return fetch_data("""
        SELECT order_date,
               SUM(total_amount) AS revenue
        FROM orders_1
        GROUP BY order_date;
    """, ["Date", "Revenue"])

# ---------------- PRODUCTS ---------------- #
def top_products():
    return fetch_data("""
        SELECT p.product_name,
               SUM(oi.quantity) AS total_sold
        FROM order_items_1 oi
        JOIN products_1 p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY total_sold DESC;
    """, ["Product", "Sold"])

def product_contribution():
    return fetch_data("""
        SELECT p.product_name,
               SUM(oi.quantity * oi.price) AS revenue,
               ROUND(
                   SUM(oi.quantity * oi.price) * 100 /
                   (SELECT SUM(total_amount) FROM orders_1), 2
               ) AS contribution_percent
        FROM order_items_1 oi
        JOIN products_1 p ON oi.product_id = p.product_id
        GROUP BY p.product_name;
    """, ["Product", "Revenue", "Contribution %"])

# ---------------- CUSTOMERS ---------------- #
def top_customers():
    return fetch_data("""
        SELECT c.name,
               SUM(o.total_amount) AS total_spent
        FROM customers_1 c
        JOIN orders_1 o ON c.customer_id = o.customer_id
        GROUP BY c.name
        ORDER BY total_spent DESC;
    """, ["Customer", "Spent"])

def repeat_customers():
    return fetch_data("""
        SELECT customer_id,
               COUNT(order_id) AS orders
        FROM orders_1
        GROUP BY customer_id
        HAVING COUNT(order_id) > 1;
    """, ["Customer ID", "Orders"])

# ---------------- CATEGORY ---------------- #
def category_sales():
    return fetch_data("""
        SELECT cat.category_name,
               SUM(oi.quantity * oi.price) AS revenue
        FROM order_items_1 oi
        JOIN products_1 p ON oi.product_id = p.product_id
        JOIN categories_1 cat ON p.category_id = cat.category_id
        GROUP BY cat.category_name;
    """, ["Category", "Revenue"])

# ---------------- PROFIT ---------------- #
def profit_analysis():
    return fetch_data("""
        SELECT p.product_name,
               SUM(oi.quantity * (oi.price - p.cost_price)) AS profit
        FROM order_items_1 oi
        JOIN products_1 p ON oi.product_id = p.product_id
        GROUP BY p.product_name
        ORDER BY profit DESC;
    """, ["Product", "Profit"])