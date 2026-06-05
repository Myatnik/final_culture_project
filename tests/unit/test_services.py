import unittest
import os
import packages.core.database as db_module
from packages.core.services import (
    calculate_stay_price,
    get_next_room_status,
    register_guest,
    create_stay,
    get_available_room_by_category,
    occupy_room,
    checkout_guest,
    get_room_status,
)
from packages.core.database import init_db, get_connection

TEST_DB = "test_hotel.db"


class TestCalculateStayPrice(unittest.TestCase):
    def test_calculates_total_for_room_only(self):
        base_price = 3500.0
        nights = 2
        services = []
        self.assertEqual(calculate_stay_price(base_price, nights, services), 7000.0)

    def test_calculates_total_with_services(self):
        base_price = 3500.0
        nights = 2
        services = [{'price': 800.0}]
        self.assertEqual(calculate_stay_price(base_price, nights, services), 8600.0)

    def test_raises_error_for_zero_nights(self):
        with self.assertRaises(ValueError) as cm:
            calculate_stay_price(3500.0, 0, [])
        self.assertIn("positive", str(cm.exception))

    def test_raises_error_for_negative_nights(self):
        with self.assertRaises(ValueError) as cm:
            calculate_stay_price(3500.0, -1, [])
        self.assertIn("positive", str(cm.exception))


class TestRoomStatusTransitions(unittest.TestCase):
    def test_available_transitions_to_cleaning(self):
        self.assertEqual(get_next_room_status('available'), 'cleaning')

    def test_cleaning_transitions_to_maintenance(self):
        self.assertEqual(get_next_room_status('cleaning'), 'maintenance')

    def test_maintenance_transitions_to_available(self):
        self.assertEqual(get_next_room_status('maintenance'), 'available')

    def test_occupied_returns_default_status(self):
        self.assertEqual(get_next_room_status('occupied'), 'available')


class TestGuestRegistration(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        db_module.DB_NAME = TEST_DB
        init_db()

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_registers_guest_successfully(self):
        guest_id = register_guest("Ivan", "Petrov", "+79161111111", "test@mail.ru")
        self.assertGreater(guest_id, 0)

    def test_raises_error_for_empty_first_name(self):
        with self.assertRaises(ValueError) as cm:
            register_guest("", "Petrov", "+79161111111", "test@mail.ru")
        self.assertIn("empty", str(cm.exception))

    def test_raises_error_for_empty_last_name(self):
        with self.assertRaises(ValueError) as cm:
            register_guest("Ivan", "", "+79161111111", "test@mail.ru")
        self.assertIn("empty", str(cm.exception))


class TestStayAndCheckout(unittest.TestCase):
    def setUp(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)
        db_module.DB_NAME = TEST_DB
        init_db()

    def tearDown(self):
        if os.path.exists(TEST_DB):
            os.remove(TEST_DB)

    def test_occupy_room_changes_status_to_occupied(self):
        room = get_available_room_by_category(1)
        self.assertEqual(get_room_status(room['room_id']), 'available')
        occupy_room(room['room_id'])
        self.assertEqual(get_room_status(room['room_id']), 'occupied')

    def test_checkout_updates_guest_spending_and_room_status(self):
        guest_id = register_guest("Anna", "Sidorova", "+79162222222", "anna@mail.ru")
        room = get_available_room_by_category(1)
        create_stay(guest_id, room['room_id'], "2025-01-01", "2025-01-03", 7000.0)
        occupy_room(room['room_id'])

        checkout_guest(1)

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT total_spent FROM guests WHERE guest_id=?", (guest_id,))
        self.assertEqual(cur.fetchone()['total_spent'], 7000.0)
        self.assertEqual(get_room_status(room['room_id']), 'cleaning')
        conn.close()


if __name__ == "__main__":
    unittest.main()
