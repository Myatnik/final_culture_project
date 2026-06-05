import sqlite3
import os
DB_NAME = os.environ.get("HOTEL_DB_PATH", "hotel.db")

def get_connection():
    """Create database connection with foreign keys support."""
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database schema and seed data."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS room_categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name TEXT NOT NULL,
            base_price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS rooms (
            room_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_number TEXT NOT NULL UNIQUE,
            category_id INTEGER REFERENCES room_categories(category_id),
            floor INTEGER NOT NULL,
            status TEXT DEFAULT 'available'
        );

        CREATE TABLE IF NOT EXISTS guests (
            guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            total_spent REAL DEFAULT 0.0,
            registration_date DATE DEFAULT (DATE('now'))
        );

        CREATE TABLE IF NOT EXISTS stays (
            stay_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_id INTEGER REFERENCES guests(guest_id),
            room_id INTEGER REFERENCES rooms(room_id),
            check_in_date DATE NOT NULL,
            check_out_date DATE NOT NULL,
            stay_status TEXT DEFAULT 'active',
            total_price REAL,
            payment_status TEXT DEFAULT 'paid',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS staff (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            position TEXT,
            phone TEXT,
            hire_date DATE
        );

        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS room_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER REFERENCES rooms(room_id),
            staff_id INTEGER REFERENCES staff(staff_id),
            task_type TEXT NOT NULL,
            task_date DATE DEFAULT (DATE('now')),
            status TEXT DEFAULT 'pending'
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM room_categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('Standard', 3500.00),
            ('Comfort', 5000.00),
            ('Luxury', 8500.00),
            ('Economy', 2500.00)
        ]
        cursor.executemany("INSERT INTO room_categories (category_name, base_price) VALUES (?, ?)", categories)

        rooms = [
            ('101', 1, 1, 'available'),
            ('102', 1, 1, 'available'),
            ('201', 2, 2, 'available'),
            ('202', 2, 2, 'available'),
            ('301', 3, 3, 'available'),
            ('302', 3, 3, 'available'),
            ('401', 4, 4, 'available'),
            ('105', 4, 1, 'available')
        ]
        cursor.executemany("INSERT INTO rooms (room_number, category_id, floor, status) VALUES (?, ?, ?, ?)", rooms)

        staff = [
            ('Olga', 'Volkova', 'administrator', '+79161112233', '2023-03-15'),
            ('Natalia', 'Pomidorova', 'cleaner', '+79033334455', '2024-01-10'),
            ('Sergey', 'Morozov', 'cleaner', '+79154445566', '2025-02-20'),
            ('Nikolay', 'Yakovlev', 'maintenance_worker', '+79031112233', '2024-06-15'),
            ('Anna', 'Sokolova', 'administrator', '+79265556677', '2024-08-01')
        ]
        cursor.executemany("INSERT INTO staff (first_name, last_name, position, phone, hire_date) VALUES (?, ?, ?, ?, ?)", staff)

        services = [
            ('Breakfast', 800.00),
            ('SPA', 3500.00),
            ('Transfer', 2500.00),
            ('Mini-bar', 1200.00),
            ('Laundry', 500.00)
        ]
        cursor.executemany("INSERT INTO services (service_name, price) VALUES (?, ?)", services)

    conn.commit()
    conn.close()
