from datetime import datetime, timedelta
from .database import get_connection

def get_next_room_status(current_status):
    """Get next status in room lifecycle."""
    status_flow = {
        'available': 'cleaning',
        'cleaning': 'maintenance',
        'maintenance': 'available'
    }
    return status_flow.get(current_status, 'available')

def calculate_stay_price(base_price, nights, services):
    """Calculate total price for stay.

    Args:
        base_price: Room price per night
        nights: Number of nights
        services: List of dicts with 'price' key

    Returns:
        Total price
    """
    room_total = base_price * nights
    services_total = sum(svc['price'] * nights for svc in services)
    return room_total + services_total

def get_available_room_by_category(category_id):
    """Get first available room in category."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT room_id FROM rooms WHERE category_id=? AND status='available' LIMIT 1",
        (category_id,)
    )
    room = cur.fetchone()
    conn.close()
    return room

def get_room_categories():
    """Get all room categories."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category_id, category_name, base_price FROM room_categories")
    categories = cur.fetchall()
    conn.close()
    return categories

def get_services():
    """Get all available services."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT service_id, service_name, price FROM services")
    services = cur.fetchall()
    conn.close()
    return services

def register_guest(first_name, last_name, phone, email):
    """Register new guest in database."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO guests (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)",
        (first_name, last_name, phone, email)
    )
    guest_id = cur.lastrowid
    conn.commit()
    conn.close()
    return guest_id

def create_stay(guest_id, room_id, check_in_date, check_out_date, total_price):
    """Create new stay record."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO stays (guest_id, room_id, check_in_date, check_out_date, total_price, payment_status) VALUES (?, ?, ?, ?, ?, ?)",
        (guest_id, room_id, check_in_date, check_out_date, total_price, 'paid')
    )
    stay_id = cur.lastrowid
    conn.commit()
    conn.close()
    return stay_id

def occupy_room(room_id):
    """Mark room as occupied."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET status='occupied' WHERE room_id=?", (room_id,))
    conn.commit()
    conn.close()

def update_room_status(room_id, status):
    """Update room status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE rooms SET status=? WHERE room_id=?", (status, room_id))
    conn.commit()
    conn.close()

def get_room_status(room_id):
    """Get current room status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
    result = cur.fetchone()
    conn.close()
    return result['status'] if result else None

def get_staff_by_position(position):
    """Get staff members by position."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT staff_id, first_name, last_name FROM staff WHERE position=?",
        (position,)
    )
    staff = cur.fetchall()
    conn.close()
    return staff

def get_rooms_for_task(task_type):
    """Get rooms available for task assignment."""
    conn = get_connection()
    cur = conn.cursor()
    if task_type == "cleaning":
        cur.execute(
            "SELECT room_id, room_number FROM rooms WHERE status IN ('available', 'occupied', 'cleaning') ORDER BY room_number"
        )
    else:
        cur.execute(
            "SELECT room_id, room_number FROM rooms WHERE status IN ('available', 'cleaning', 'maintenance') ORDER BY room_number"
        )
    rooms = cur.fetchall()
    conn.close()
    return rooms

def assign_task(room_id, staff_id, task_type):
    """Assign task to staff for room."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO room_tasks (room_id, staff_id, task_type) VALUES (?, ?, ?)",
        (room_id, staff_id, task_type)
    )
    conn.commit()
    conn.close()

def get_pending_tasks(task_type):
    """Get pending tasks of specific type."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT ct.task_id, r.room_number, s.first_name || ' ' || s.last_name as staff_name, ct.task_date, ct.status
        FROM room_tasks ct
        JOIN rooms r ON ct.room_id = r.room_id
        JOIN staff s ON ct.staff_id = s.staff_id
        WHERE ct.task_type=? AND ct.status != 'completed'
        ORDER BY ct.task_date DESC
    """, (task_type,))
    tasks = cur.fetchall()
    conn.close()
    return tasks

def complete_task(task_id):
    """Mark task as completed and update room status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT room_id FROM room_tasks WHERE task_id=?", (task_id,))
    res = cur.fetchone()
    if res:
        cur.execute("UPDATE room_tasks SET status='completed' WHERE task_id=?", (task_id,))
        cur.execute("SELECT status FROM rooms WHERE room_id=?", (res['room_id'],))
        if cur.fetchone()['status'] != 'occupied':
            cur.execute("UPDATE rooms SET status='available' WHERE room_id=?", (res['room_id'],))
    conn.commit()
    conn.close()

def get_all_stays():
    """Get all stays with guest and room info."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.stay_id, g.first_name || ' ' || g.last_name as guest_name, r.room_number, 
               s.check_in_date, s.check_out_date, s.total_price, s.payment_status 
        FROM stays s 
        JOIN guests g ON s.guest_id = g.guest_id 
        JOIN rooms r ON s.room_id = r.room_id 
        ORDER BY s.stay_id DESC
    """)
    stays = cur.fetchall()
    conn.close()
    return stays

def checkout_guest(stay_id):
    """Check out guest and update records."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT guest_id, room_id, total_price FROM stays WHERE stay_id=?", (stay_id,))
    res = cur.fetchone()
    if res:
        cur.execute(
            "UPDATE guests SET total_spent = COALESCE(total_spent, 0) + ? WHERE guest_id=?",
            (res['total_price'], res['guest_id'])
        )
        cur.execute(
            "UPDATE rooms SET status='cleaning' WHERE room_id=? AND status='occupied'",
            (res['room_id'],)
        )
        cur.execute("DELETE FROM stays WHERE stay_id=?", (stay_id,))
    conn.commit()
    conn.close()

def get_all_guests(search_term=None):
    """Get all guests or search by last name."""
    conn = get_connection()
    cur = conn.cursor()
    if search_term:
        cur.execute(
            "SELECT * FROM guests WHERE last_name LIKE ? ORDER BY last_name",
            (f"%{search_term}%",)
        )
    else:
        cur.execute("SELECT * FROM guests ORDER BY last_name")
    guests = cur.fetchall()
    conn.close()
    return guests

def get_dashboard_stats():
    """Get statistics for dashboard."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM rooms")
    total_rooms = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM rooms WHERE status = 'occupied'")
    occupied = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total_price), 0) FROM stays WHERE payment_status='paid'")
    active_rev = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(total_spent), 0) FROM guests")
    history_rev = cur.fetchone()[0]

    conn.close()

    return {
        'total_rooms': total_rooms,
        'occupied': occupied,
        'available': total_rooms - occupied,
        'revenue': active_rev + history_rev
    }

def get_rooms_with_categories():
    """Get all rooms with category info."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT r.room_id, r.room_number, r.status, rc.category_name, r.floor 
        FROM rooms r 
        JOIN room_categories rc ON r.category_id = rc.category_id 
        ORDER BY r.floor, r.room_number
    """)
    rooms = cur.fetchall()
    conn.close()
    return rooms
