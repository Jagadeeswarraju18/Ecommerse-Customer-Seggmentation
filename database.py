

import sqlite3
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os
import random
import json

DATABASE = 'customer_analytics.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_db_connection()
    
    # Users table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_otps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            otp TEXT NOT NULL,
            expiry_time DATETIME NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
                ''')
    # Enhanced Customers table with more analytics fields
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            city TEXT,
            city_tier INTEGER DEFAULT 1,
            gender TEXT,
            marital_status TEXT,
            preferred_login_device TEXT DEFAULT 'Mobile',
            preferred_order_category TEXT DEFAULT 'Fashion',
            tenure INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_churned BOOLEAN DEFAULT 0,
            satisfaction_score INTEGER DEFAULT 3,
            complain BOOLEAN DEFAULT 0,
            total_spent REAL DEFAULT 0,
            total_orders INTEGER DEFAULT 0,
            days_since_last_order INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Products table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            description TEXT,
            stock INTEGER DEFAULT 0,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Enhanced Orders table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            product_id INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            order_value REAL,
            quantity INTEGER,
            category TEXT,
            status TEXT DEFAULT 'completed',
            cashback_amount REAL DEFAULT 0,
            payment_method TEXT DEFAULT 'Credit Card',
            shipping_cost REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
            FOREIGN KEY (product_id) REFERENCES products (product_id)
        )
    ''')
    
    # Customer segments table for RFM analysis
    conn.execute('''
        CREATE TABLE IF NOT EXISTS customer_segments (
            segment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            segment_name TEXT,
            recency_score INTEGER,
            frequency_score INTEGER,
            monetary_score INTEGER,
            rfm_score TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_realistic_customers():
    """Create realistic customers with varied registration dates and demographics"""
    conn = get_db_connection()
    
    # Check current customer count
    customer_count = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
    
    if customer_count < 50:  # Create 50+ customers for better analytics
        
        # Realistic customer data
        first_names = ['John', 'Jane', 'Mike', 'Sarah', 'David', 'Emily', 'Chris', 'Anna', 'James', 'Lisa',
                      'Robert', 'Maria', 'William', 'Jennifer', 'Richard', 'Patricia', 'Charles', 'Linda',
                      'Thomas', 'Barbara', 'Daniel', 'Elizabeth', 'Matthew', 'Susan', 'Anthony', 'Jessica',
                      'Mark', 'Karen', 'Donald', 'Nancy', 'Steven', 'Betty', 'Paul', 'Dorothy', 'Andrew',
                      'Helen', 'Kenneth', 'Sandra', 'Joshua', 'Donna', 'Kevin', 'Carol', 'Brian', 'Ruth',
                      'George', 'Sharon', 'Edward', 'Michelle', 'Ronald', 'Laura', 'Timothy', 'Sarah']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                     'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
                     'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
                     'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
                     'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores']
        
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio',
                 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville', 'Fort Worth', 'Columbus',
                 'Charlotte', 'San Francisco', 'Indianapolis', 'Seattle', 'Denver', 'Washington DC',
                 'Boston', 'El Paso', 'Nashville', 'Detroit', 'Oklahoma City', 'Portland', 'Las Vegas',
                 'Memphis', 'Louisville', 'Baltimore', 'Milwaukee', 'Albuquerque', 'Tucson', 'Fresno',
                 'Mesa', 'Sacramento', 'Atlanta', 'Kansas City', 'Colorado Springs', 'Omaha']
        
        categories = ['Fashion', 'Electronics', 'Home & Kitchen', 'Sports', 'Books', 'Beauty']
        devices = ['Mobile', 'Desktop', 'Tablet']
        genders = ['Male', 'Female']
        marital_statuses = ['Single', 'Married', 'Divorced']
        
        customers_to_create = 60 - customer_count  # Create up to 60 customers
        
        for i in range(customers_to_create):
            # Generate realistic customer data
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            full_name = f"{first_name} {last_name}"
            username = f"{first_name.lower()}{last_name.lower()}{random.randint(1, 999)}"
            email = f"{username}@example.com"
            
            # Registration date: 1-24 months ago with weighted distribution (more recent)
            weight = random.random()
            if weight < 0.4:  # 40% registered in last 3 months
                days_ago = random.randint(1, 90)
            elif weight < 0.7:  # 30% registered 3-6 months ago
                days_ago = random.randint(91, 180)
            elif weight < 0.9:  # 20% registered 6-12 months ago
                days_ago = random.randint(181, 365)
            else:  # 10% registered 12-24 months ago
                days_ago = random.randint(366, 730)
            
            registration_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if user already exists
            existing_user = conn.execute('''
                SELECT * FROM users WHERE username = ? OR email = ?
            ''', (username, email)).fetchone()
            
            if not existing_user:
                # Create user
                password_hash = generate_password_hash('customer123')
                cursor = conn.execute('''
                    INSERT INTO users (username, email, password_hash, role, created_at)
                    VALUES (?, ?, ?, 'customer', ?)
                ''', (username, email, password_hash, registration_date))
                
                user_id = cursor.lastrowid
                
                # Create customer profile
                city = random.choice(cities)
                city_tier = random.choices([1, 2, 3], weights=[60, 30, 10])[0]  # Weighted city tiers
                
                # Last seen date (some customers more active than others)
                activity_weight = random.random()
                if activity_weight < 0.3:  # 30% very active (last seen within 7 days)
                    last_seen_days = random.randint(0, 7)
                elif activity_weight < 0.6:  # 30% moderately active (7-30 days)
                    last_seen_days = random.randint(8, 30)
                elif activity_weight < 0.8:  # 20% less active (30-90 days)
                    last_seen_days = random.randint(31, 90)
                else:  # 20% inactive (90+ days)
                    last_seen_days = random.randint(91, 200)
                
                last_seen = (datetime.now() - timedelta(days=last_seen_days)).strftime('%Y-%m-%d %H:%M:%S')
                
                # Determine if churned (inactive for 90+ days)
                is_churned = 1 if last_seen_days >= 90 else 0
                
                conn.execute('''
                    INSERT INTO customers (user_id, name, email, phone, city, gender, marital_status, 
                                         city_tier, preferred_login_device, preferred_order_category,
                                         created_at, last_seen, is_churned, satisfaction_score, complain)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, full_name, email, f"555-{random.randint(1000, 9999)}", city,
                     random.choice(genders), random.choice(marital_statuses), city_tier,
                     random.choice(devices), random.choice(categories), registration_date,
                     last_seen, is_churned, random.randint(1, 5), random.choice([0, 0, 0, 1])))
        
        print(f"✅ Created {customers_to_create} realistic customers with varied demographics and timing")
    
    conn.commit()
    conn.close()

def create_sample_products():
    """Create comprehensive product catalog"""
    conn = get_db_connection()
    
    products_exist = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()['count']
    
    if products_exist < 30:  # Create more products for better analytics
        sample_products = [
            # Electronics
            ('iPhone 15 Pro', 'Electronics', 999.99, 'Latest iPhone with advanced camera system', 25),
            ('Samsung Galaxy S24', 'Electronics', 849.99, 'Premium Android smartphone', 30),
            ('MacBook Air M2', 'Electronics', 1199.99, 'Lightweight laptop for professionals', 15),
            ('Dell XPS 13', 'Electronics', 999.99, 'Compact Windows laptop', 20),
            ('iPad Pro 12.9"', 'Electronics', 1099.99, 'Professional tablet for creativity', 18),
            ('AirPods Pro 2nd Gen', 'Electronics', 249.99, 'Premium wireless earbuds', 50),
            ('Sony WH-1000XM5', 'Electronics', 399.99, 'Noise-canceling headphones', 35),
            ('Apple Watch Series 9', 'Electronics', 399.99, 'Advanced smartwatch', 40),
            ('Nintendo Switch OLED', 'Electronics', 349.99, 'Portable gaming console', 25),
            ('PlayStation 5', 'Electronics', 499.99, 'Next-gen gaming console', 10),
            
            # Fashion
            ('Nike Air Max 270', 'Fashion', 130.00, 'Comfortable running shoes', 45),
            ('Adidas Ultraboost 22', 'Fashion', 180.00, 'Premium running shoes', 35),
            ('Levi\'s 501 Jeans', 'Fashion', 89.99, 'Classic denim jeans', 60),
            ('Ralph Lauren Polo Shirt', 'Fashion', 79.99, 'Premium cotton polo', 40),
            ('North Face Jacket', 'Fashion', 199.99, 'Weather-resistant outdoor jacket', 25),
            ('Ray-Ban Aviators', 'Fashion', 154.99, 'Classic sunglasses', 30),
            ('Calvin Klein Watch', 'Fashion', 149.99, 'Elegant dress watch', 20),
            ('Coach Handbag', 'Fashion', 295.00, 'Luxury leather handbag', 15),
            ('Nike Sportswear Hoodie', 'Fashion', 65.00, 'Comfortable cotton hoodie', 50),
            ('Converse Chuck Taylor', 'Fashion', 55.00, 'Classic canvas sneakers', 55),
            
            # Home & Kitchen
            ('KitchenAid Stand Mixer', 'Home & Kitchen', 379.99, 'Professional stand mixer', 12),
            ('Instant Pot Duo 7-in-1', 'Home & Kitchen', 99.99, 'Multi-use pressure cooker', 25),
            ('Nespresso Coffee Machine', 'Home & Kitchen', 199.99, 'Premium coffee maker', 20),
            ('Dyson V15 Vacuum', 'Home & Kitchen', 749.99, 'Cordless stick vacuum', 8),
            ('Le Creuset Dutch Oven', 'Home & Kitchen', 329.99, 'Cast iron cooking pot', 15),
            ('All-Clad Cookware Set', 'Home & Kitchen', 599.99, 'Professional cookware set', 10),
            ('Vitamix Blender', 'Home & Kitchen', 449.99, 'High-performance blender', 18),
            ('Herman Miller Aeron Chair', 'Home & Kitchen', 1395.00, 'Ergonomic office chair', 5),
            ('IKEA Dining Table', 'Home & Kitchen', 249.99, 'Modern dining table', 8),
            ('Casper Mattress Queen', 'Home & Kitchen', 1095.00, 'Memory foam mattress', 6),
            
            # Sports & Fitness
            ('Peloton Bike+', 'Sports', 2495.00, 'Interactive exercise bike', 3),
            ('Bowflex Dumbbells', 'Sports', 349.99, 'Adjustable dumbbells set', 12),
            ('Yeti Rambler Tumbler', 'Sports', 34.99, 'Insulated travel mug', 75),
            ('Wilson Tennis Racket', 'Sports', 159.99, 'Professional tennis racket', 20),
            ('Spalding Basketball', 'Sports', 29.99, 'Official size basketball', 40),
            ('Under Armour Gym Bag', 'Sports', 49.99, 'Durable sports bag', 35),
            ('Fitbit Charge 5', 'Sports', 179.99, 'Advanced fitness tracker', 30),
            ('Yoga Mat Premium', 'Sports', 79.99, 'Non-slip exercise mat', 45),
            ('Resistance Bands Set', 'Sports', 24.99, 'Home workout equipment', 60),
            ('Protein Powder', 'Sports', 39.99, 'Whey protein supplement', 50),
            
            # Beauty & Personal Care
            ('Dyson Hair Dryer', 'Beauty', 429.99, 'Professional hair styling tool', 15),
            ('Fenty Beauty Foundation', 'Beauty', 38.00, 'Inclusive shade range foundation', 40),
            ('The Ordinary Skincare Set', 'Beauty', 45.99, 'Complete skincare routine', 35),
            ('Charlotte Tilbury Lipstick', 'Beauty', 37.00, 'Luxury matte lipstick', 30),
            ('Olaplex Hair Treatment', 'Beauty', 28.00, 'Professional hair repair', 25),
            
            # Books & Media
            ('Atomic Habits Book', 'Books', 13.99, 'Best-selling self-help book', 100),
            ('The Psychology of Money', 'Books', 14.99, 'Financial wisdom book', 80),
            ('Dune Complete Series', 'Books', 49.99, 'Classic sci-fi book set', 25),
            ('MasterClass Annual', 'Books', 180.00, 'Online learning subscription', 200),
            ('Kindle Paperwhite', 'Electronics', 139.99, 'E-reader with backlight', 45)
        ]
        
        # Product images from Unsplash - relevant to each product
        product_images = {
            # Electronics
            'iPhone 15 Pro': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop&crop=center',
            'Samsung Galaxy S24': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop&crop=center',
            'MacBook Air M2': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop&crop=center',
            'Dell XPS 13': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop&crop=center',
            'iPad Pro 12.9"': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop&crop=center',
            'AirPods Pro 2nd Gen': 'https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&h=400&fit=crop&crop=center',
            'Sony WH-1000XM5': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop&crop=center',
            'Apple Watch Series 9': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&crop=center',
            'Nintendo Switch OLED': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=400&h=400&fit=crop&crop=center',
            'PlayStation 5': 'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400&h=400&fit=crop&crop=center',
            'Kindle Paperwhite': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop&crop=center',
            
            # Fashion
            'Nike Air Max 270': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&crop=center',
            'Adidas Ultraboost 22': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop&crop=center',
            'Levi\'s 501 Jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop&crop=center',
            'Ralph Lauren Polo Shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop&crop=center',
            'North Face Jacket': 'https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?w=400&h=400&fit=crop&crop=center',
            'Ray-Ban Aviators': 'https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400&h=400&fit=crop&crop=center',
            'Calvin Klein Watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&crop=center',
            'Coach Handbag': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400&h=400&fit=crop&crop=center',
            'Nike Sportswear Hoodie': 'https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400&h=400&fit=crop&crop=center',
            'Converse Chuck Taylor': 'https://images.unsplash.com/photo-1514989940723-e8e51635b782?w=400&h=400&fit=crop&crop=center',
            
            # Home & Kitchen
            'KitchenAid Stand Mixer': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop&crop=center',
            'Instant Pot Duo 7-in-1': 'https://images.unsplash.com/photo-1585515656473-a63123bb558e?w=400&h=400&fit=crop&crop=center',
            'Nespresso Coffee Machine': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&h=400&fit=crop&crop=center',
            'Dyson V15 Vacuum': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop&crop=center',
            'Le Creuset Dutch Oven': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop&crop=center',
            'All-Clad Cookware Set': 'https://images.unsplash.com/photo-1593618998160-e34014d4f117?w=400&h=400&fit=crop&crop=center',
            'Vitamix Blender': 'https://images.unsplash.com/photo-1570197788417-0e82375c9371?w=400&h=400&fit=crop&crop=center',
            'Herman Miller Aeron Chair': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&crop=center',
            'IKEA Dining Table': 'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400&h=400&fit=crop&crop=center',
            'Casper Mattress Queen': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop&crop=center',
            
            # Sports & Fitness
            'Peloton Bike+': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop&crop=center',
            'Bowflex Dumbbells': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop&crop=center',
            'Yeti Rambler Tumbler': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&crop=center',
            'Wilson Tennis Racket': 'https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=400&h=400&fit=crop&crop=center',
            'Spalding Basketball': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400&h=400&fit=crop&crop=center',
            'Under Armour Gym Bag': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop&crop=center',
            'Fitbit Charge 5': 'https://images.unsplash.com/photo-1557935728-e6d1eaabe2db?w=400&h=400&fit=crop&crop=center',
            'Yoga Mat Premium': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop&crop=center',
            'Resistance Bands Set': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400&h=400&fit=crop&crop=center',
            'Protein Powder': 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&h=400&fit=crop&crop=center',
            
            # Beauty & Personal Care
            'Dyson Hair Dryer': 'https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400&h=400&fit=crop&crop=center',
            'Fenty Beauty Foundation': 'https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400&h=400&fit=crop&crop=center',
            'The Ordinary Skincare Set': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop&crop=center',
            'Charlotte Tilbury Lipstick': 'https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400&h=400&fit=crop&crop=center',
            'Olaplex Hair Treatment': 'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop&crop=center',
            
            # Books & Media
            'Atomic Habits Book': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop&crop=center',
            'The Psychology of Money': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop&crop=center',
            'Dune Complete Series': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=400&fit=crop&crop=center',
            'MasterClass Annual': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=400&h=400&fit=crop&crop=center',
        }
        
        for product in sample_products:
            name, category, price, description, stock = product
            # Get the relevant image for this product, or use a default
            image_path = product_images.get(name, 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400&h=400&fit=crop&crop=center')
            
            conn.execute('''
                INSERT INTO products (name, category, price, description, stock, image_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, category, price, description, stock, image_path))
        
        print(f"✅ Created {len(sample_products)} diverse products across categories")
    
    conn.commit()
    conn.close()

def create_realistic_orders():
    """Create realistic orders with seasonal patterns and customer behavior"""
    conn = get_db_connection()
    
    # Check if orders exist
    orders_exist = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    
    if orders_exist < 100:  # Create substantial order history
        # Get customers and products
        customers = conn.execute('''
            SELECT customer_id, created_at, preferred_order_category, is_churned 
            FROM customers
        ''').fetchall()
        products = conn.execute('SELECT product_id, price, category, name FROM products').fetchall()
        
        if customers and products:
            all_orders = []
            
            # Define seasonal multipliers for realistic patterns
            seasonal_multipliers = {
                1: 0.8,   # January (post-holiday slump)
                2: 0.9,   # February
                3: 1.0,   # March
                4: 1.1,   # April (spring shopping)
                5: 1.2,   # May
                6: 1.0,   # June
                7: 0.9,   # July
                8: 1.0,   # August
                9: 1.1,   # September (back to school)
                10: 1.2,  # October
                11: 1.5,  # November (Black Friday)
                12: 1.8   # December (Holiday season)
            }
            
            for customer in customers:
                customer_id = customer['customer_id']
                preferred_category = customer['preferred_order_category']
                is_churned = customer['is_churned']
                
                # Parse customer creation date
                if customer['created_at']:
                    customer_start_date = datetime.strptime(customer['created_at'][:19], '%Y-%m-%d %H:%M:%S')
                else:
                    customer_start_date = datetime.now() - timedelta(days=365)
                
                # Determine customer segment behavior
                if is_churned:
                    # Churned customers: fewer orders, mostly early in their lifecycle
                    base_orders = random.randint(1, 5)
                    order_timeframe_ratio = 0.3  # Orders concentrated in first 30% of their lifecycle
                else:
                    # Active customers: more orders throughout their lifecycle
                    days_since_registration = (datetime.now() - customer_start_date).days
                    if days_since_registration < 30:
                        base_orders = random.randint(1, 3)  # New customers
                    elif days_since_registration < 90:
                        base_orders = random.randint(2, 8)  # Getting engaged
                    else:
                        base_orders = random.randint(3, 15)  # Established customers
                    order_timeframe_ratio = 1.0
                
                # Create orders for this customer
                days_since_registration = max(1, (datetime.now() - customer_start_date).days)
                order_period = int(days_since_registration * order_timeframe_ratio)
                
                for _ in range(base_orders):
                    # Random order date within the customer's active period
                    days_after_registration = random.randint(1, order_period)
                    order_date = customer_start_date + timedelta(days=days_after_registration)
                    
                    # Don't create future orders
                    if order_date > datetime.now():
                        order_date = datetime.now() - timedelta(days=random.randint(1, 30))
                    
                    # Apply seasonal multiplier to order probability
                    month = order_date.month
                    seasonal_mult = seasonal_multipliers.get(month, 1.0)
                    
                    # Skip some orders based on seasonal patterns
                    if random.random() > seasonal_mult:
                        continue
                    
                    # Choose products (prefer customer's category, but sometimes buy others)
                    available_products = products
                    if random.random() < 0.7:  # 70% chance to buy from preferred category
                        preferred_products = [p for p in products if p['category'] == preferred_category]
                        if preferred_products:
                            available_products = preferred_products
                    
                    # Multiple items per order sometimes
                    items_in_order = random.choices([1, 2, 3, 4], weights=[60, 25, 10, 5])[0]
                    
                    order_total = 0
                    for _ in range(items_in_order):
                        product = random.choice(available_products)
                        quantity = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
                        
                        # Price variations (sales, discounts, etc.)
                        price_modifier = random.uniform(0.8, 1.1)  # ±20% price variation
                        
                        # Higher discounts during high-season months
                        if month in [11, 12]:  # November, December
                            price_modifier *= random.uniform(0.7, 0.9)  # Additional discounts
                        
                        item_total = product['price'] * quantity * price_modifier
                        order_total += item_total
                        
                        # Shipping cost (free over $50, otherwise $5-15)
                        shipping_cost = 0 if order_total > 50 else random.uniform(5, 15)
                        
                        payment_methods = ['Credit Card', 'Debit Card', 'PayPal', 'Apple Pay', 'Cash on Delivery']
                        payment_method = random.choices(payment_methods, weights=[40, 25, 15, 10, 10])[0]
                        
                        all_orders.append((
                            customer_id,
                            product['product_id'],
                            order_date.strftime('%Y-%m-%d %H:%M:%S'),
                            round(item_total, 2),
                            quantity,
                            product['category'],
                            'completed',
                            round(random.uniform(0, item_total * 0.05), 2),  # 0-5% cashback
                            payment_method,
                            round(shipping_cost, 2)
                        ))
            
            # Sort orders by date for realistic timeline
            all_orders.sort(key=lambda x: x[2])
            
            # Insert orders in batches
            batch_size = 100
            for i in range(0, len(all_orders), batch_size):
                batch = all_orders[i:i + batch_size]
                conn.executemany('''
                    INSERT INTO orders (customer_id, product_id, order_date, order_value, 
                                      quantity, category, status, cashback_amount, payment_method, shipping_cost)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch)
                conn.commit()
            
            print(f"✅ Created {len(all_orders)} realistic orders with seasonal patterns")
            
            # Update customer statistics
            update_customer_statistics()
    
    conn.commit()
    conn.close()

def update_customer_statistics():
    """Update customer total_spent, total_orders, and days_since_last_order"""
    conn = get_db_connection()
    
    customers = conn.execute('SELECT customer_id FROM customers').fetchall()
    
    for customer in customers:
        customer_id = customer['customer_id']
        
        # Calculate total spent and orders
        stats = conn.execute('''
            SELECT 
                COUNT(*) as total_orders,
                SUM(order_value) as total_spent,
                MAX(order_date) as last_order_date
            FROM orders 
            WHERE customer_id = ?
        ''', (customer_id,)).fetchone()
        
        total_orders = stats['total_orders'] or 0
        total_spent = stats['total_spent'] or 0
        last_order_date = stats['last_order_date']
        
        # Calculate days since last order
        if last_order_date:
            last_order = datetime.strptime(last_order_date[:19], '%Y-%m-%d %H:%M:%S')
            days_since_last_order = (datetime.now() - last_order).days
        else:
            days_since_last_order = 999  # Never ordered
        
        # Update customer record
        conn.execute('''
            UPDATE customers 
            SET total_spent = ?, total_orders = ?, days_since_last_order = ?
            WHERE customer_id = ?
        ''', (total_spent, total_orders, days_since_last_order, customer_id))
    
    conn.commit()
    conn.close()
    print("✅ Updated customer statistics")

def create_customer_segments():
    """Create RFM-based customer segments"""
    conn = get_db_connection()
    
    # Clear existing segments
    conn.execute('DELETE FROM customer_segments')
    
    # Get customer data for RFM analysis
    customers_data = conn.execute('''
        SELECT 
            c.customer_id,
            c.total_spent as monetary,
            c.total_orders as frequency,
            c.days_since_last_order as recency,
            c.created_at
        FROM customers c
        WHERE c.total_orders > 0
    ''').fetchall()
    
    if not customers_data:
        print("⚠️ No customer order data found for segmentation")
        conn.close()
        return
    
    # Calculate RFM scores and segments
    for customer in customers_data:
        customer_id = customer['customer_id']
        monetary = customer['monetary'] or 0
        frequency = customer['frequency'] or 0
        recency = customer['recency'] or 999
        
        # RFM Scoring (1-5 scale)
        # Recency: Lower days = higher score
        if recency <= 30:
            recency_score = 5
        elif recency <= 60:
            recency_score = 4
        elif recency <= 90:
            recency_score = 3
        elif recency <= 180:
            recency_score = 2
        else:
            recency_score = 1
        
        # Frequency: More orders = higher score
        if frequency >= 10:
            frequency_score = 5
        elif frequency >= 7:
            frequency_score = 4
        elif frequency >= 4:
            frequency_score = 3
        elif frequency >= 2:
            frequency_score = 2
        else:
            frequency_score = 1
        
        # Monetary: More spent = higher score
        if monetary >= 1000:
            monetary_score = 5
        elif monetary >= 500:
            monetary_score = 4
        elif monetary >= 200:
            monetary_score = 3
        elif monetary >= 50:
            monetary_score = 2
        else:
            monetary_score = 1
        
        # Create RFM score string
        rfm_score = f"{recency_score}{frequency_score}{monetary_score}"
        
        # Determine segment based on RFM scores
        avg_score = (recency_score + frequency_score + monetary_score) / 3
        
        if avg_score >= 4.5:
            segment_name = "Champions"
        elif avg_score >= 4.0:
            segment_name = "Loyal Customers"
        elif avg_score >= 3.5:
            segment_name = "Potential Loyalists"
        elif avg_score >= 3.0:
            segment_name = "New Customers"
        elif avg_score >= 2.5:
            segment_name = "Promising"
        elif avg_score >= 2.0:
            segment_name = "Need Attention"
        elif avg_score >= 1.5:
            segment_name = "About to Sleep"
        else:
            segment_name = "At Risk"
        
        # Insert segment
        conn.execute('''
            INSERT INTO customer_segments (customer_id, segment_name, recency_score, 
                                         frequency_score, monetary_score, rfm_score)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (customer_id, segment_name, recency_score, frequency_score, monetary_score, rfm_score))
    
    conn.commit()
    conn.close()
    print("✅ Created customer segments based on RFM analysis")

def create_default_admin():
    """Create default admin user"""
    conn = get_db_connection()
    
    admin_exists = conn.execute('SELECT * FROM users WHERE role = "admin"').fetchone()
    
    if not admin_exists:
        admin_password = generate_password_hash('admin123')
        conn.execute('''
            INSERT INTO users (username, email, password_hash, role, created_at)
            VALUES ('admin', 'admin@smartshop.com', ?, 'admin', ?)
        ''', (admin_password, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print("✅ Admin user created: username=admin, password=admin123")
    
    conn.commit()
    conn.close()

def initialize_comprehensive_database():
    """Initialize database with comprehensive realistic data"""
    print("🔄 Initializing comprehensive database with realistic data...")
    
    # Create directories
    os.makedirs('static/uploads', exist_ok=True)
    
    # Initialize database structure
    init_db()
    print("✅ Database structure created")
    
    # Create users and customers
    create_default_admin()
    create_realistic_customers()
    
    # Create products
    create_sample_products()
    
    # Create orders with realistic patterns
    create_realistic_orders()
    
    # Create customer segments
    create_customer_segments()
    
    # Print summary
    conn = get_db_connection()
    
    customers = conn.execute('SELECT COUNT(*) as count FROM customers').fetchone()['count']
    products = conn.execute('SELECT COUNT(*) as count FROM products').fetchone()['count']
    orders = conn.execute('SELECT COUNT(*) as count FROM orders').fetchone()['count']
    segments = conn.execute('SELECT COUNT(*) as count FROM customer_segments').fetchone()['count']
    
    # Revenue summary
    total_revenue = conn.execute('SELECT SUM(order_value) as total FROM orders').fetchone()['total'] or 0
    
    # Customer segments summary
    segment_summary = conn.execute('''
        SELECT segment_name, COUNT(*) as count 
        FROM customer_segments 
        GROUP BY segment_name 
        ORDER BY count DESC
    ''').fetchall()
    
    conn.close()
    
    print("\n" + "="*50)
    print("🎉 COMPREHENSIVE DATABASE INITIALIZATION COMPLETE!")
    print("="*50)
    print(f"📊 Data Summary:")
    print(f"   • {customers} customers with realistic demographics")
    print(f"   • {products} products across multiple categories")
    print(f"   • {orders} orders with seasonal patterns")
    print(f"   • {segments} customer segments (RFM analysis)")
    print(f"   • ${total_revenue:,.2f} total revenue generated")
    print(f"\n🎯 Customer Segments:")
    for segment in segment_summary:
        print(f"   • {segment['segment_name']}: {segment['count']} customers")
    
    print(f"\n🔐 Admin Access:")
    print(f"   • Username: admin")
    print(f"   • Password: admin123")
    print(f"   • URL: /admin")
    
    print(f"\n📈 Analytics Available:")
    print(f"   • Real-time revenue tracking")
    print(f"   • Customer segmentation analysis")
    print(f"   • Churn prediction")
    print(f"   • Seasonal sales patterns")
    print(f"   • Customer lifetime value")
    
    print("="*50)

if __name__ == '__main__':
    initialize_comprehensive_database()