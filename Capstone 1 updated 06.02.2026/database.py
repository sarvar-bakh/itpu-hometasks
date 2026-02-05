import sqlite3
import pandas as pd
import random
import threading
from datetime import datetime, timedelta
import json
from contextlib import contextmanager


class ThreadSafeDatabase:
    """Thread-safe SQLite database manager"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_name = "business_data.db"
            self.thread_local = threading.local()
            self._init_database()
            self.initialized = True

    def get_connection(self):
        """Get or create a thread-local connection"""
        if not hasattr(self.thread_local, "conn"):
            self.thread_local.conn = sqlite3.connect(
                self.db_name,
                check_same_thread=False,
                timeout=10
            )
            # Enable foreign keys and better performance
            self.thread_local.conn.execute("PRAGMA foreign_keys = ON")
            self.thread_local.conn.execute("PRAGMA journal_mode = WAL")
        return self.thread_local.conn

    @contextmanager
    def get_cursor(self):
        """Context manager for getting a cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    def _init_database(self):
        """Initialize database tables"""
        with self.get_cursor() as cursor:
            # Create sales table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS sales
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               date
                               TEXT,
                               product
                               TEXT,
                               category
                               TEXT,
                               region
                               TEXT,
                               quantity
                               INTEGER,
                               revenue
                               REAL,
                               profit
                               REAL,
                               customer_id
                               TEXT
                           )
                           ''')

            # Create customers table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS customers
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               customer_id
                               TEXT
                               UNIQUE,
                               name
                               TEXT,
                               email
                               TEXT,
                               region
                               TEXT,
                               join_date
                               TEXT,
                               loyalty_score
                               INTEGER
                           )
                           ''')

            # Create support_tickets table
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS support_tickets
                           (
                               id
                               INTEGER
                               PRIMARY
                               KEY
                               AUTOINCREMENT,
                               ticket_id
                               TEXT
                               UNIQUE,
                               title
                               TEXT,
                               description
                               TEXT,
                               status
                               TEXT
                               DEFAULT
                               'Open',
                               priority
                               TEXT
                               DEFAULT
                               'Medium',
                               created_date
                               TEXT,
                               assigned_to
                               TEXT
                           )
                           ''')

            # Check and generate sample data
            cursor.execute("SELECT COUNT(*) FROM sales")
            count = cursor.fetchone()[0]

            if count < 500:
                self._generate_sample_data(cursor, 600)

    def _generate_sample_data(self, cursor, num_records):
        """Generate sample data"""
        products = ["Laptop", "Smartphone", "Tablet", "Monitor", "Keyboard",
                    "Mouse", "Headphones", "Printer", "Router", "Camera"]
        categories = ["Electronics", "Computers", "Accessories", "Networking", "Photography"]
        regions = ["North", "South", "East", "West", "Central"]

        print(f"Generating {num_records} sample records...")

        # Generate sales data
        sales_data = []
        for i in range(num_records):
            date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            product = random.choice(products)
            category = random.choice(categories)
            region = random.choice(regions)
            quantity = random.randint(1, 10)
            revenue = round(random.uniform(100, 5000), 2)
            profit = round(revenue * random.uniform(0.1, 0.4), 2)
            customer_id = f"CUST{random.randint(1000, 9999)}"

            sales_data.append((date, product, category, region, quantity, revenue, profit, customer_id))

        cursor.executemany('''
                           INSERT INTO sales (date, product, category, region, quantity, revenue, profit, customer_id)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                           ''', sales_data)

        # Generate customer data
        customer_ids = list(set([s[7] for s in sales_data]))[:100]  # Get unique customer IDs
        customers_data = []
        for cust_id in customer_ids:
            name = f"Customer {random.randint(1, 1000)}"
            email = f"{name.lower().replace(' ', '.')}@example.com"
            region = random.choice(regions)
            join_date = (datetime.now() - timedelta(days=random.randint(0, 1095))).strftime('%Y-%m-%d')
            loyalty_score = random.randint(1, 100)

            customers_data.append((cust_id, name, email, region, join_date, loyalty_score))

        cursor.executemany('''
                           INSERT
                           OR IGNORE INTO customers (customer_id, name, email, region, join_date, loyalty_score)
            VALUES (?, ?, ?, ?, ?, ?)
                           ''', customers_data)

        print(f"Generated {num_records} sales records and {len(customer_ids)} customer records")

    def get_database_stats(self):
        """Get database statistics"""
        stats = {}

        with self.get_cursor() as cursor:
            # Table counts
            for table in ['sales', 'customers', 'support_tickets']:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[f"{table}_count"] = cursor.fetchone()[0]

            # Sales stats
            cursor.execute("SELECT SUM(revenue), SUM(profit), AVG(revenue) FROM sales")
            total_rev, total_profit, avg_rev = cursor.fetchone()
            stats["total_revenue"] = round(total_rev or 0, 2)
            stats["total_profit"] = round(total_profit or 0, 2)
            stats["avg_sale"] = round(avg_rev or 0, 2)

            # Customer stats
            cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM sales")
            stats["unique_customers"] = cursor.fetchone()[0]

            # Top products
            cursor.execute("""
                           SELECT product, SUM(quantity) as total_qty
                           FROM sales
                           GROUP BY product
                           ORDER BY total_qty DESC LIMIT 5
                           """)
            stats["top_products"] = cursor.fetchall()

        return stats

    def execute_query(self, query, params=None):
        """Execute a safe SQL query"""
        # Safety check - only allow SELECT queries
        query_lower = query.strip().lower()

        # Block dangerous operations
        dangerous_operations = ['drop', 'delete', 'truncate', 'alter', 'update', 'insert']
        if any(op in query_lower for op in dangerous_operations):
            raise PermissionError("This operation is not allowed for safety reasons.")

        if not query_lower.startswith('select'):
            raise PermissionError("Only SELECT queries are allowed for data safety.")

        with self.get_cursor() as cursor:
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Get column names
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                results = cursor.fetchall()

                return {
                    "success": True,
                    "data": results,
                    "columns": columns,
                    "row_count": len(results)
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }

    def get_schema_info(self):
        """Get database schema"""
        schema = {}

        with self.get_cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                schema[table] = [col[1] for col in columns]

        return schema

    def create_support_ticket(self, title, description, priority="Medium"):
        """Create a support ticket"""
        with self.get_cursor() as cursor:
            ticket_id = f"TICKET-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                           INSERT INTO support_tickets (ticket_id, title, description, priority, created_date)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (ticket_id, title, description, priority, created_date))

            return {
                "success": True,
                "ticket_id": ticket_id,
                "message": f"Support ticket '{ticket_id}' created successfully."
            }

    def close_all_connections(self):
        """Close all database connections"""
        if hasattr(self.thread_local, "conn"):
            self.thread_local.conn.close()
            del self.thread_local.conn


# Global instance
db_instance = ThreadSafeDatabase()