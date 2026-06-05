"""
Smoke tests for Hotel Management System
These tests verify basic functionality without extensive edge cases
"""

import sys
import os
import json
import sqlite3
import tempfile
from datetime import datetime, timedelta

# Add project root to path so that 'main' module can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# ---------- Mock tkinter (BEFORE importing main) ----------
def setup_mock_tkinter():
    """Replace tkinter and its submodules with mocks for testing"""
    
    class MockTk:
        def __init__(self):
            self.title_called = None
            self.geometry_called = None
            self.configure_called = None
        def title(self, text):
            self.title_called = text
        def geometry(self, size):
            self.geometry_called = size
        def configure(self, **kwargs):
            self.configure_called = kwargs
        def mainloop(self):
            pass
    
    class MockFrame:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
            self.children = []
        def pack(self, **kwargs):
            pass
        def pack_propagate(self, flag):
            pass
        def grid(self, **kwargs):
            pass
        def destroy(self):
            pass
    
    class MockLabel:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
        def pack(self, **kwargs):
            pass
        def grid(self, **kwargs):
            pass
    
    class MockButton:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
            self.command = kwargs.get('command')
        def pack(self, **kwargs):
            pass
        def grid(self, **kwargs):
            pass
    
    class MockEntry:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
            self.text = ""
        def pack(self, **kwargs):
            pass
        def grid(self, **kwargs):
            pass
        def insert(self, pos, text):
            self.text = text
        def get(self):
            return self.text
        def bind(self, event, handler):
            pass
    
    class MockCombobox:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
            self.values = []
            self.current_index = -1
        def pack(self, **kwargs):
            pass
        def grid(self, **kwargs):
            pass
        def bind(self, event, handler):
            pass
        def current(self, index=None):
            if index is not None:
                self.current_index = index
            return self.current_index
        def set(self, value):
            pass
    
    class MockTreeview:
        def __init__(self, parent=None, **kwargs):
            self.parent = parent
            self.kwargs = kwargs
            self.children = {}
        def pack(self, **kwargs):
            pass
        def grid(self, **kwargs):
            pass
        def heading(self, col, text=None):
            pass
        def column(self, col, **kwargs):
            pass
        def insert(self, parent, index, **kwargs):
            pass
        def delete(self, *items):
            pass
        def selection(self):
            return ()
        def item(self, item, **kwargs):
            return {}
        def yview(self, *args):
            pass
        def bind(self, event, handler):
            pass
        def get_children(self, item=''):
            return []
    
    # Create mock messagebox
    class MockMessagebox:
        @staticmethod
        def showinfo(*args, **kwargs):
            pass
        @staticmethod
        def showerror(*args, **kwargs):
            pass
        @staticmethod
        def showwarning(*args, **kwargs):
            pass
        @staticmethod
        def askyesno(*args, **kwargs):
            return True
    
    # Create mock simpledialog
    class MockSimpleDialog:
        @staticmethod
        def askstring(*args, **kwargs):
            return ""
        @staticmethod
        def askinteger(*args, **kwargs):
            return 0
    
    # Build the main mock tkinter module
    mock_tkinter = type('MockTkinter', (), {
        'Tk': MockTk,
        'Frame': MockFrame,
        'Label': MockLabel,
        'Button': MockButton,
        'Entry': MockEntry,
        'END': 'end',
        'VERTICAL': 'vertical',
        'HORIZONTAL': 'horizontal',
        'BOTH': 'both',
        'LEFT': 'left',
        'RIGHT': 'right',
        'TOP': 'top',
        'BOTTOM': 'bottom',
        'X': 'x',
        'Y': 'y',
        'EW': 'ew',
        'NS': 'ns'
    })()
    
    # Add ttk submodule with Combobox and Treeview
    mock_ttk = type('MockTtk', (), {
        'Combobox': MockCombobox,
        'Treeview': MockTreeview
    })()
    mock_tkinter.ttk = mock_ttk
    
    # Add messagebox and simpledialog
    mock_tkinter.messagebox = MockMessagebox
    mock_tkinter.simpledialog = MockSimpleDialog
    
    # Also add the standalone ttk module (for import tkinter.ttk)
    sys.modules['tkinter.ttk'] = mock_ttk
    
    # Replace the real tkinter with our mock
    sys.modules['tkinter'] = mock_tkinter


# Apply mocks before importing main
setup_mock_tkinter()

# Now import the real application module
import main

# ---------- Test infrastructure ----------
FIXTURES_DIR = os.path.join(current_dir, '..', 'fixtures')

class TestDatabase:
    """Helper class for database operations during testing"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    def init_test_db(self):
        """Initialize database with schema from fixture data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Load schema from fixture
        schema_path = os.path.join(FIXTURES_DIR, 'schema.json')
        with open(schema_path, 'r') as f:
            schema = json.load(f)
            cursor.executescript(schema['create_tables'])
        
        # Insert test data
        categories_path = os.path.join(FIXTURES_DIR, 'categories.json')
        with open(categories_path, 'r') as f:
            categories = json.load(f)
            for cat in categories:
                cursor.execute(
                    "INSERT INTO room_categories (category_id, category_name, base_price) VALUES (?, ?, ?)",
                    (cat['category_id'], cat['category_name'], cat['base_price'])
                )
        
        rooms_path = os.path.join(FIXTURES_DIR, 'rooms.json')
        with open(rooms_path, 'r') as f:
            rooms = json.load(f)
            for room in rooms:
                cursor.execute(
                    "INSERT INTO rooms (room_id, room_number, category_id, floor, status) VALUES (?, ?, ?, ?, ?)",
                    (room['room_id'], room['room_number'], room['category_id'], room['floor'], room['status'])
                )
        
        guests_path = os.path.join(FIXTURES_DIR, 'guests.json')
        with open(guests_path, 'r') as f:
            guests = json.load(f)
            for guest in guests:
                cursor.execute(
                    "INSERT INTO guests (guest_id, first_name, last_name, phone, email, total_spent) VALUES (?, ?, ?, ?, ?, ?)",
                    (guest['guest_id'], guest['first_name'], guest['last_name'], guest['phone'], guest['email'], guest['total_spent'])
                )
        
        staff_path = os.path.join(FIXTURES_DIR, 'staff.json')
        with open(staff_path, 'r') as f:
            staff_list = json.load(f)
            for staff in staff_list:
                cursor.execute(
                    "INSERT INTO staff (staff_id, first_name, last_name, position, phone, hire_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (staff['staff_id'], staff['first_name'], staff['last_name'], staff['position'], staff['phone'], staff['hire_date'])
                )
        
        services_path = os.path.join(FIXTURES_DIR, 'services.json')
        with open(services_path, 'r') as f:
            services = json.load(f)
            for service in services:
                cursor.execute(
                    "INSERT INTO services (service_id, service_name, price) VALUES (?, ?, ?)",
                    (service['service_id'], service['service_name'], service['price'])
                )
        
        stays_path = os.path.join(FIXTURES_DIR, 'stays.json')
        with open(stays_path, 'r') as f:
            stays = json.load(f)
            for stay in stays:
                cursor.execute(
                    "INSERT INTO stays (stay_id, guest_id, room_id, check_in_date, check_out_date, total_price, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (stay['stay_id'], stay['guest_id'], stay['room_id'], stay['check_in_date'], stay['check_out_date'], stay['total_price'], stay['payment_status'])
                )
        
        tasks_path = os.path.join(FIXTURES_DIR, 'room_tasks.json')
        with open(tasks_path, 'r') as f:
            tasks = json.load(f)
            for task in tasks:
                cursor.execute(
                    "INSERT INTO room_tasks (task_id, room_id, staff_id, task_type, task_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                    (task['task_id'], task['room_id'], task['staff_id'], task['task_type'], task['task_date'], task['status'])
                )
        
        conn.commit()
        conn.close()


def setup_test_db():
    """Create a temporary test database with fixture data"""
    temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
    temp_db.close()
    
    test_db = TestDatabase(temp_db.name)
    test_db.init_test_db()
    
    return test_db


# ---------- Smoke Tests ----------
def test_connection():
    """Test 1: Verify database connection works"""
    print("Running test_connection...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM rooms")
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count > 0, "Database should have rooms"
    print("[PASS] Connection test passed - found", count, "rooms")
    
    os.unlink(test_db.db_path)


def test_room_categories():
    """Test 2: Verify room categories are loaded correctly"""
    print("Running test_room_categories...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    categories_path = os.path.join(FIXTURES_DIR, 'categories.json')
    with open(categories_path, 'r') as f:
        expected_categories = json.load(f)
    
    cursor.execute("SELECT category_name, base_price FROM room_categories ORDER BY category_id")
    actual_categories = cursor.fetchall()
    
    assert len(actual_categories) == len(expected_categories), f"Expected {len(expected_categories)} categories, got {len(actual_categories)}"
    
    for i, expected in enumerate(expected_categories):
        assert actual_categories[i]['category_name'] == expected['category_name'], f"Category name mismatch: expected {expected['category_name']}, got {actual_categories[i]['category_name']}"
        assert actual_categories[i]['base_price'] == expected['base_price'], f"Base price mismatch for {expected['category_name']}"
    
    conn.close()
    print("[PASS] Room categories test passed -", len(actual_categories), "categories verified")
    os.unlink(test_db.db_path)


def test_rooms_availability():
    """Test 3: Verify room status counts match fixture data"""
    print("Running test_rooms_availability...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    rooms_path = os.path.join(FIXTURES_DIR, 'rooms.json')
    with open(rooms_path, 'r') as f:
        rooms_data = json.load(f)
    
    expected_status_counts = {}
    for room in rooms_data:
        status = room['status']
        expected_status_counts[status] = expected_status_counts.get(status, 0) + 1
    
    cursor.execute("""
        SELECT status, COUNT(*) as count 
        FROM rooms 
        GROUP BY status
    """)
    actual_counts = cursor.fetchall()
    
    for row in actual_counts:
        status = row['status']
        actual_count = row['count']
        expected_count = expected_status_counts.get(status, 0)
        assert actual_count == expected_count, f"Status '{status}' count mismatch: expected {expected_count}, got {actual_count}"
    
    conn.close()
    print("[PASS] Room availability test passed - status counts verified")
    os.unlink(test_db.db_path)


def test_guest_registration_flow():
    """Test 4: Verify guest registration process"""
    print("Running test_guest_registration_flow...")
    test_db = setup_test_db()
    
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    # Save initial counts
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='available'")
    available_before = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='occupied'")
    occupied_before = cursor.fetchone()[0]
    
    # Simulate guest registration
    cursor.execute("""
        INSERT INTO guests (first_name, last_name, phone, email) 
        VALUES (?, ?, ?, ?)
    """, ('John', 'Doe', '+123456789', 'john@example.com'))
    guest_id = cursor.lastrowid
    
    cursor.execute("SELECT room_id FROM rooms WHERE status='available' LIMIT 1")
    room = cursor.fetchone()
    assert room is not None, "No available rooms found"
    room_id = room['room_id']
    
    check_in = datetime.now().strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
    
    cursor.execute("""
        INSERT INTO stays (guest_id, room_id, check_in_date, check_out_date, total_price, payment_status) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (guest_id, room_id, check_in, check_out, 7000.00, 'paid'))
    
    cursor.execute("UPDATE rooms SET status='occupied' WHERE room_id=?", (room_id,))
    
    # Verify changes
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='available'")
    available_after = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM rooms WHERE status='occupied'")
    occupied_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM guests WHERE last_name='Doe'")
    guest_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM stays WHERE guest_id=?", (guest_id,))
    stay_count = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    # Correct assertions
    assert available_after == available_before - 1, f"Available rooms: expected {available_before - 1}, got {available_after}"
    assert occupied_after == occupied_before + 1, f"Occupied rooms: expected {occupied_before + 1}, got {occupied_after}"
    assert guest_count == 1, "Guest was not inserted"
    assert stay_count == 1, "Stay record was not created"
    
    print("[PASS] Guest registration test passed")
    os.unlink(test_db.db_path)


def test_checkout_flow():
    """Test 5: Verify checkout process moves room to cleaning"""
    print("Running test_checkout_flow...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO guests (first_name, last_name, phone) 
        VALUES (?, ?, ?)
    """, ('Jane', 'Smith', '+987654321'))
    guest_id = cursor.lastrowid
    
    cursor.execute("SELECT room_id FROM rooms WHERE status='occupied' LIMIT 1")
    room = cursor.fetchone()
    assert room is not None, "No occupied rooms found in fixture"
    room_id = room['room_id']
    
    cursor.execute("""
        INSERT INTO stays (guest_id, room_id, check_in_date, check_out_date, total_price, payment_status) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (guest_id, room_id, '2026-01-01', '2026-01-03', 10000.00, 'paid'))
    stay_id = cursor.lastrowid
    
    cursor.execute("UPDATE guests SET total_spent = COALESCE(total_spent, 0) + ? WHERE guest_id=?", (10000.00, guest_id))
    cursor.execute("UPDATE rooms SET status='cleaning' WHERE room_id=? AND status='occupied'", (room_id,))
    cursor.execute("DELETE FROM stays WHERE stay_id=?", (stay_id,))
    
    conn.commit()
    
    cursor.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
    room_status = cursor.fetchone()['status']
    
    cursor.execute("SELECT total_spent FROM guests WHERE guest_id=?", (guest_id,))
    total_spent = cursor.fetchone()['total_spent']
    
    conn.close()
    
    assert room_status == 'cleaning', f"Room status should be 'cleaning', got '{room_status}'"
    assert total_spent >= 10000.00, "Total spent should be updated"
    
    print("[PASS] Checkout flow test passed")
    os.unlink(test_db.db_path)


def test_task_assignment():
    """Test 6: Verify task assignment updates room status"""
    print("Running test_task_assignment...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT room_id FROM rooms WHERE status='available' LIMIT 1")
    room = cursor.fetchone()
    assert room is not None, "No available rooms found"
    room_id = room['room_id']
    
    cursor.execute("SELECT staff_id FROM staff WHERE position='cleaner' LIMIT 1")
    staff = cursor.fetchone()
    assert staff is not None, "No cleaner staff found"
    staff_id = staff['staff_id']
    
    cursor.execute("""
        INSERT INTO room_tasks (room_id, staff_id, task_type, status) 
        VALUES (?, ?, ?, ?)
    """, (room_id, staff_id, 'cleaning', 'pending'))
    
    cursor.execute("UPDATE rooms SET status='cleaning' WHERE room_id=?", (room_id,))
    
    conn.commit()
    
    cursor.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
    room_status = cursor.fetchone()['status']
    
    cursor.execute("SELECT COUNT(*) FROM room_tasks WHERE room_id=? AND status='pending'", (room_id,))
    task_count = cursor.fetchone()[0]
    
    conn.close()
    
    assert room_status == 'cleaning', "Room status should be 'cleaning' after task assignment"
    assert task_count == 1, "Task was not created"
    
    print("[PASS] Task assignment test passed")
    os.unlink(test_db.db_path)


def test_complete_task():
    """Test 7: Verify completing a task returns room to available"""
    print("Running test_complete_task...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT room_id FROM rooms WHERE status='cleaning' LIMIT 1")
    room = cursor.fetchone()
    
    if not room:
        cursor.execute("SELECT room_id FROM rooms WHERE status='available' LIMIT 1")
        room = cursor.fetchone()
        room_id = room['room_id']
        
        cursor.execute("SELECT staff_id FROM staff WHERE position='cleaner' LIMIT 1")
        staff = cursor.fetchone()
        staff_id = staff['staff_id']
        
        cursor.execute("""
            INSERT INTO room_tasks (room_id, staff_id, task_type, status) 
            VALUES (?, ?, ?, ?)
        """, (room_id, staff_id, 'cleaning', 'pending'))
        
        cursor.execute("UPDATE rooms SET status='cleaning' WHERE room_id=?", (room_id,))
        conn.commit()
    else:
        room_id = room['room_id']
    
    cursor.execute("SELECT task_id FROM room_tasks WHERE room_id=? AND status='pending'", (room_id,))
    task = cursor.fetchone()
    task_id = task['task_id']
    
    cursor.execute("UPDATE room_tasks SET status='completed' WHERE task_id=?", (task_id,))
    
    cursor.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
    current_status = cursor.fetchone()['status']
    if current_status != 'occupied':
        cursor.execute("UPDATE rooms SET status='available' WHERE room_id=?", (room_id,))
    
    conn.commit()
    
    cursor.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
    room_status = cursor.fetchone()['status']
    
    cursor.execute("SELECT status FROM room_tasks WHERE task_id=?", (task_id,))
    task_status = cursor.fetchone()['status']
    
    conn.close()
    
    assert task_status == 'completed', "Task should be marked as completed"
    assert room_status == 'available', f"Room should be 'available' after task completion, got '{room_status}'"
    
    print("[PASS] Complete task test passed")
    os.unlink(test_db.db_path)


def test_guest_search():
    """Test 8: Verify guest search functionality"""
    print("Running test_guest_search...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM guests WHERE last_name LIKE ?", ('%T%',))
    results = cursor.fetchall()
    
    assert len(results) > 0, "Search should return at least one result"
    
    for row in results:
        assert 't' in row['last_name'].lower() or 'T' in row['last_name'], f"Search returned non-matching record: {row['last_name']}"
    
    conn.close()
    print("[PASS] Guest search test passed - found", len(results), "matching guests")
    os.unlink(test_db.db_path)


def test_revenue_calculation():
    """Test 9: Verify revenue calculation from stays and guest spending"""
    print("Running test_revenue_calculation...")
    test_db = setup_test_db()
    conn = test_db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COALESCE(SUM(total_price), 0) FROM stays WHERE payment_status='paid'")
    stays_revenue = cursor.fetchone()[0]
    
    cursor.execute("SELECT COALESCE(SUM(total_spent), 0) FROM guests")
    guests_revenue = cursor.fetchone()[0]
    
    total_revenue = stays_revenue + guests_revenue
    
    guests_path = os.path.join(FIXTURES_DIR, 'guests.json')
    with open(guests_path, 'r') as f:
        guests_data = json.load(f)
        expected_guest_spending = sum(g['total_spent'] for g in guests_data)
    
    stays_path = os.path.join(FIXTURES_DIR, 'stays.json')
    with open(stays_path, 'r') as f:
        stays_data = json.load(f)
        expected_stays_revenue = sum(s['total_price'] for s in stays_data if s['payment_status'] == 'paid')
    
    expected_total = expected_guest_spending + expected_stays_revenue
    
    assert stays_revenue == expected_stays_revenue, f"Stays revenue mismatch: expected {expected_stays_revenue}, got {stays_revenue}"
    assert guests_revenue == expected_guest_spending, f"Guests spending mismatch: expected {expected_guest_spending}, got {guests_revenue}"
    assert total_revenue == expected_total, f"Total revenue mismatch: expected {expected_total}, got {total_revenue}"
    
    conn.close()
    print("[PASS] Revenue calculation test passed - Total:", total_revenue, "RUB")
    os.unlink(test_db.db_path)


def run_all_smoke_tests():
    """Run all smoke tests and report results"""
    print("\n" + "="*60)
    print("SMOKE TESTS FOR HOTEL MANAGEMENT SYSTEM")
    print("="*60 + "\n")
    
    tests = [
        ("Database Connection", test_connection),
        ("Room Categories", test_room_categories),
        ("Room Availability", test_rooms_availability),
        ("Guest Registration Flow", test_guest_registration_flow),
        ("Checkout Flow", test_checkout_flow),
        ("Task Assignment", test_task_assignment),
        ("Complete Task", test_complete_task),
        ("Guest Search", test_guest_search),
        ("Revenue Calculation", test_revenue_calculation),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print("[FAIL]", test_name, "FAILED:", str(e))
            failed += 1
        except Exception as e:
            print("[ERROR]", test_name, "ERROR:", str(e))
            failed += 1
        print()
    
    print("="*60)
    print("SMOKE TEST SUMMARY:", passed, "passed,", failed, "failed,", passed+failed, "total")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_smoke_tests()
    sys.exit(0 if success else 1)