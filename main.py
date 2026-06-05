import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "hotel.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
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
            status TEXT DEFAULT 'свободен'
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
            stay_status TEXT DEFAULT 'активно',
            total_price REAL,
            payment_status TEXT DEFAULT 'оплачено',
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
            status TEXT DEFAULT 'ожидает'
        );
    """)

    cursor.execute("SELECT COUNT(*) FROM room_categories")
    if cursor.fetchone()[0] == 0:
        categories = [
            ('Стандарт', 3500.00),
            ('Комфорт', 5000.00),
            ('Люкс', 8500.00),
            ('Эконом', 2500.00)
        ]
        cursor.executemany("INSERT INTO room_categories (category_name, base_price) VALUES (?, ?)", categories)

        rooms = [
            ('101', 1, 1, 'свободен'),
            ('102', 1, 1, 'свободен'),
            ('201', 2, 2, 'свободен'),
            ('202', 2, 2, 'уборка'),
            ('301', 3, 3, 'свободен'),
            ('302', 3, 3, 'ремонт'),
            ('401', 4, 4, 'свободен'),
            ('105', 4, 1, 'свободен')
        ]
        cursor.executemany("INSERT INTO rooms (room_number, category_id, floor, status) VALUES (?, ?, ?, ?)", rooms)

        guests = [
            ('Иван', 'Петров', '+79161234567', 'ivan.petrov@mail.ru', 0.0),
            ('Мария', 'Сидорова', '+79262345678', 'maria.s@gmail.com', 0.0)
        ]
        cursor.executemany("INSERT INTO guests (first_name, last_name, phone, email, total_spent) VALUES (?, ?, ?, ?, ?)", guests)

        staff = [
            ('Ольга', 'Волкова', 'администратор', '+79161112233', '2023-03-15'),
            ('Наталья', 'Помидорова', 'уборщик', '+79033334455', '2024-01-10'),
            ('Сергей', 'Морозов', 'уборщик', '+79154445566', '2025-02-20'),
            ('Николай', 'Яковлев', 'ремонтник', '+79031112233', '2024-06-15'),
            ('Анна', 'Соколова', 'администратор', '+79265556677', '2024-08-01')
        ]
        cursor.executemany("INSERT INTO staff (first_name, last_name, position, phone, hire_date) VALUES (?, ?, ?, ?, ?)", staff)

        services = [
            ('Завтрак', 800.00),
            ('СПА', 3500.00),
            ('Трансфер', 2500.00),
            ('Мини-бар', 1200.00),
            ('Прачечная', 500.00)
        ]
        cursor.executemany("INSERT INTO services (service_name, price) VALUES (?, ?)", services)

        cursor.execute("INSERT INTO stays (guest_id, room_id, check_in_date, check_out_date, stay_status, total_price, payment_status) VALUES (1, 1, '2026-05-20', '2026-05-25', 'активно', 17500.00, 'оплачено')")
        cursor.execute("UPDATE rooms SET status='занят' WHERE room_id=1")

    conn.commit()
    conn.close()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Система управления отелем")
        self.geometry("1120x720")
        self.resizable(False, False)
        self.configure(bg="#f0f0f0")
        init_db()
        self.create_header()
        self.create_navigation()
        self.create_content_area()
        self.show_dashboard()

    def create_header(self):
        header_frame = tk.Frame(self, bg="#2c3e50", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        label = tk.Label(header_frame, text="СИСТЕМА УПРАВЛЕНИЯ ОТЕЛЕМ", font=("Arial", 20, "bold"), fg="white", bg="#2c3e50")
        label.pack(side="left", padx=20, pady=10)

    def create_navigation(self):
        nav_frame = tk.Frame(self, bg="#34495e", width=200)
        nav_frame.pack(side="left", fill="y")
        nav_frame.pack_propagate(False)
        buttons = [
            ("Главная", self.show_dashboard),
            ("Регистрация", self.show_registration),
            ("Уборка", self.show_cleaning),
            ("Ремонт", self.show_maintenance),
            ("Проживания", self.show_stays),
            ("Гости", self.show_guests),
        ]
        for text, command in buttons:
            btn = tk.Button(nav_frame, text=text, font=("Arial", 12), bg="#34495e", fg="white", activebackground="#465f75", activeforeground="white", bd=0, anchor="w", padx=20, pady=15, command=command)
            btn.pack(fill="x")

    def create_content_area(self):
        self.content_frame = tk.Frame(self, bg="white")
        self.content_frame.pack(side="right", fill="both", expand=True)

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_content()
        title = tk.Label(self.content_frame, text="Панель управления", font=("Arial", 18, "bold"), bg="white", fg="#2c3e50")
        title.pack(pady=10, anchor="w", padx=20)

        stats_frame = tk.Frame(self.content_frame, bg="white")
        stats_frame.pack(fill="x", padx=20)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rooms")
        total_rooms = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM rooms WHERE status = 'занят'")
        occupied = cur.fetchone()[0]
        available = total_rooms - occupied

        cur.execute("SELECT COALESCE(SUM(total_price), 0) FROM stays WHERE payment_status='оплачено'")
        active_rev = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(total_spent), 0) FROM guests")
        history_rev = cur.fetchone()[0]
        revenue = active_rev + history_rev
        conn.close()

        self.create_stat_card(stats_frame, "Всего номеров", str(total_rooms), "#3498db", 0)
        self.create_stat_card(stats_frame, "Занято", str(occupied), "#e74c3c", 1)
        self.create_stat_card(stats_frame, "Свободно", str(available), "#2ecc71", 2)
        self.create_stat_card(stats_frame, "Выручка", f"{revenue:,.2f} руб.", "#f1c40f", 3)

        tk.Label(self.content_frame, text="Карта номеров", font=("Arial", 14, "bold"), bg="white").pack(pady=(15, 5), anchor="w", padx=20)
        legend_frame = tk.Frame(self.content_frame, bg="white")
        legend_frame.pack(anchor="w", padx=20, pady=5)
        self.create_legend_dot(legend_frame, "Свободен", "#2ecc71")
        self.create_legend_dot(legend_frame, "Занят", "#e74c3c")
        self.create_legend_dot(legend_frame, "Уборка", "#f1c40f")
        self.create_legend_dot(legend_frame, "Ремонт", "#e67e22")

        grid_frame = tk.Frame(self.content_frame, bg="white")
        grid_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.render_room_grid(grid_frame)

    def create_stat_card(self, parent, title, value, color, col_index):
        frame = tk.Frame(parent, bg=color, width=200, height=100)
        frame.grid(row=0, column=col_index, padx=10, sticky="ew")
        frame.pack_propagate(False)
        lbl_title = tk.Label(frame, text=title, font=("Arial", 10), fg="white", bg=color)
        lbl_title.pack(pady=(15, 5))
        lbl_value = tk.Label(frame, text=value, font=("Arial", 18, "bold"), fg="white", bg=color)
        lbl_value.pack()

    def render_room_grid(self, parent_frame):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT r.room_id, r.room_number, r.status, rc.category_name, r.floor FROM rooms r JOIN room_categories rc ON r.category_id = rc.category_id ORDER BY r.floor, r.room_number""")
        rooms = cur.fetchall()
        conn.close()
        floors = {}
        for room in rooms:
            fl = room['floor']
            if fl not in floors: floors[fl] = []
            floors[fl].append(room)
        row_idx = 0
        for floor in sorted(floors.keys()):
            tk.Label(parent_frame, text=f"Этаж {floor}", font=("Arial", 12, "bold"), bg="white").grid(row=row_idx, column=0, sticky="w", pady=5)
            row_idx += 1
            col_idx = 1
            for room in floors[floor]:
                color_map = {'свободен': '#2ecc71', 'занят': '#e74c3c', 'уборка': '#f1c40f', 'ремонт': '#e67e22'}
                color = color_map.get(room['status'], '#95a5a6')
                btn = tk.Button(parent_frame, text=f"{room['room_number']}\n{room['category_name']}", bg=color, fg="white", width=12, height=3, command=lambda r=room['room_id']: self.toggle_room_status(r))
                btn.grid(row=row_idx, column=col_idx, padx=5, pady=5)
                col_idx += 1
            row_idx += 1

    def create_legend_dot(self, parent, text, color):
        canvas = tk.Canvas(parent, width=15, height=15, bg="white", highlightthickness=0)
        canvas.create_oval(2, 2, 13, 13, fill=color, outline=color)
        canvas.pack(side="left", padx=(0, 5))
        tk.Label(parent, text=text, bg="white").pack(side="left", padx=(0, 15))

    def toggle_room_status(self, room_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
        current_status = cur.fetchone()['status']

        if current_status == 'занят':
            messagebox.showinfo("Внимание", "Нельзя менять статус занятого номера. Сначала выселите гостя.")
            conn.close()
            self.show_dashboard()
            return

        next_status = {'свободен': 'уборка', 'уборка': 'ремонт', 'ремонт': 'свободен'}.get(current_status, 'свободен')
        cur.execute("UPDATE rooms SET status=? WHERE room_id=?", (next_status, room_id))
        conn.commit()
        conn.close()
        self.show_dashboard()

    def show_registration(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Регистрация гостя", font=("Arial", 18, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(form_frame, text="Фамилия:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_lastname = tk.Entry(form_frame, width=30)
        self.ent_lastname.grid(row=0, column=1, pady=5)
        tk.Label(form_frame, text="Имя:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_firstname = tk.Entry(form_frame, width=30)
        self.ent_firstname.grid(row=1, column=1, pady=5)
        tk.Label(form_frame, text="Телефон:", bg="white").grid(row=2, column=0, sticky="w", pady=5)
        self.ent_phone = tk.Entry(form_frame, width=30)
        self.ent_phone.grid(row=2, column=1, pady=5)
        tk.Label(form_frame, text="Email:", bg="white").grid(row=3, column=0, sticky="w", pady=5)
        self.ent_email = tk.Entry(form_frame, width=30)
        self.ent_email.grid(row=3, column=1, pady=5)
        tk.Label(form_frame, text="Дата заезда:", bg="white").grid(row=4, column=0, sticky="w", pady=5)
        self.ent_checkin = tk.Entry(form_frame, width=30)
        self.ent_checkin.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.ent_checkin.grid(row=4, column=1, pady=5)
        tk.Label(form_frame, text="Кол-во ночей:", bg="white").grid(row=5, column=0, sticky="w", pady=5)
        self.ent_nights = tk.Entry(form_frame, width=30)
        self.ent_nights.insert(0, "1")
        self.ent_nights.grid(row=5, column=1, pady=5)
        tk.Label(form_frame, text="Категория:", bg="white").grid(row=6, column=0, sticky="w", pady=5)
        cat_frame = tk.Frame(form_frame, bg="white")
        cat_frame.grid(row=6, column=1, pady=5, sticky="w")
        self.combo_cat = ttk.Combobox(cat_frame, width=25, state="readonly")
        self.combo_cat.pack(side="left")
        self.refresh_categories()
        tk.Label(form_frame, text="Доп. услуги:", bg="white").grid(row=7, column=0, sticky="nw", pady=5)
        self.services_frame = tk.Frame(form_frame, bg="white")
        self.services_frame.grid(row=7, column=1, pady=5, sticky="w")
        self.service_vars = []
        self.load_services_checkboxes()
        self.lbl_total = tk.Label(form_frame, text="Итого: 0.00 руб.", font=("Arial", 14, "bold"), bg="white", fg="#2c3e50")
        self.lbl_total.grid(row=8, column=1, sticky="e", pady=10)
        self.ent_nights.bind("<KeyRelease>", lambda e: self.update_total())
        self.combo_cat.bind("<<ComboboxSelected>>", lambda e: self.update_total())
        tk.Button(form_frame, text="ЗАРЕГИСТРИРОВАТЬ И ОПЛАТИТЬ", command=self.register_guest, bg="#27ae60", fg="white", font=("Arial", 12, "bold")).grid(row=9, column=1, sticky="e", pady=20)
        self.update_total()

    def load_services_checkboxes(self):
        for w in self.services_frame.winfo_children(): w.destroy()
        self.service_vars.clear()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT service_id, service_name, price FROM services")
        services = cur.fetchall()
        conn.close()
        for idx, svc in enumerate(services):
            var = tk.IntVar()
            chk = tk.Checkbutton(self.services_frame, text=f"{svc['service_name']} ({svc['price']} руб./ночь)", variable=var, bg="white", command=self.update_total)
            chk.grid(row=idx//2, column=idx%2, sticky="w")
            self.service_vars.append((var, svc['service_name'], svc['price']))

    def update_total(self):
        if not hasattr(self, 'ent_nights') or not hasattr(self, 'current_categories'): return
        try:
            nights = int(self.ent_nights.get())
        except ValueError:
            nights = 0
        cat_idx = self.combo_cat.current()
        base_price = self.current_categories[cat_idx]['base_price'] if cat_idx >= 0 else 0
        room_total = base_price * nights
        services_total = sum(price * nights for var, name, price in self.service_vars if var.get() == 1)
        self.lbl_total.config(text=f"Итого: {room_total + services_total:.2f} руб.")

    def register_guest(self):
        lastname = self.ent_lastname.get()
        firstname = self.ent_firstname.get()
        phone = self.ent_phone.get()
        email = self.ent_email.get()
        if not lastname or not firstname:
            messagebox.showerror("Ошибка", "Введите имя и фамилию")
            return
        try:
            nights = int(self.ent_nights.get())
            if nights <= 0:
                messagebox.showerror("Ошибка", "Количество ночей должно быть больше нуля")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное количество ночей")
            return
        cat_idx = self.combo_cat.current()
        if cat_idx < 0:
            messagebox.showerror("Ошибка", "Выберите категорию номера")
            return
        selected_cat = self.current_categories[cat_idx]
        cat_id = selected_cat['category_id']
        base_price = selected_cat['base_price']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT room_id FROM rooms WHERE category_id=? AND status='свободен' LIMIT 1", (cat_id,))
        room = cur.fetchone()
        if not room:
            messagebox.showwarning("Внимание", "Нет свободных номеров в этой категории!")
            conn.close()
            return
        room_id = room['room_id']

        cur.execute("INSERT INTO guests (first_name, last_name, phone, email) VALUES (?, ?, ?, ?)", (firstname, lastname, phone, email))
        guest_id = cur.lastrowid

        check_in = self.ent_checkin.get()
        try:
            check_out_dt = datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=nights)
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты")
            conn.close()
            return
        check_out = check_out_dt.strftime("%Y-%m-%d")

        services_total = sum(price * nights for var, name, price in self.service_vars if var.get() == 1)
        total_price = (base_price * nights) + services_total

        cur.execute("INSERT INTO stays (guest_id, room_id, check_in_date, check_out_date, total_price, payment_status) VALUES (?, ?, ?, ?, ?, ?)", 
                    (guest_id, room_id, check_in, check_out, total_price, 'оплачено'))
        
        cur.execute("UPDATE rooms SET status='занят' WHERE room_id=?", (room_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Успех", f"Гость зарегистрирован.\nНомер: {room_id}\nОплачено: {total_price} руб.")
        self.show_dashboard()

    def refresh_categories(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT category_id, category_name, base_price FROM room_categories")
        self.current_categories = cur.fetchall()
        conn.close()
        names = [c['category_name'] for c in self.current_categories]
        self.combo_cat['values'] = names
        if names: self.combo_cat.current(0)

    def show_cleaning(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Задачи уборки", font=("Arial", 18, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(form_frame, text="Номер:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_room_clean = ttk.Combobox(form_frame, width=20, state="readonly")
        self.combo_room_clean.grid(row=0, column=1, pady=5)
        tk.Label(form_frame, text="Сотрудник:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_staff_clean = ttk.Combobox(form_frame, width=20, state="readonly")
        self.combo_staff_clean.grid(row=1, column=1, pady=5)
        tk.Button(form_frame, text="Назначить уборку", command=lambda: self.assign_task("уборка"), bg="#2980b9", fg="white").grid(row=2, column=1, sticky="e", pady=10)
        self.load_dropdowns("уборка")
        self.render_tasks_tree("уборка")

    def show_maintenance(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Задачи ремонта", font=("Arial", 18, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        form_frame = tk.Frame(self.content_frame, bg="white")
        form_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(form_frame, text="Номер:", bg="white").grid(row=0, column=0, sticky="w", pady=5)
        self.combo_room_maint = ttk.Combobox(form_frame, width=20, state="readonly")
        self.combo_room_maint.grid(row=0, column=1, pady=5)
        tk.Label(form_frame, text="Сотрудник:", bg="white").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_staff_maint = ttk.Combobox(form_frame, width=20, state="readonly")
        self.combo_staff_maint.grid(row=1, column=1, pady=5)
        tk.Button(form_frame, text="Назначить ремонт", command=lambda: self.assign_task("ремонт"), bg="#2980b9", fg="white").grid(row=2, column=1, sticky="e", pady=10)
        self.load_dropdowns("ремонт")
        self.render_tasks_tree("ремонт")

    def load_dropdowns(self, task_type):
        conn = get_connection()
        cur = conn.cursor()
        combo_room = self.combo_room_clean if task_type == "уборка" else self.combo_room_maint
        combo_staff = self.combo_staff_clean if task_type == "уборка" else self.combo_staff_maint
        if task_type == "уборка":
            cur.execute("SELECT room_id, room_number FROM rooms WHERE status IN ('свободен', 'занят', 'уборка') ORDER BY room_number")
        else:
            cur.execute("SELECT room_id, room_number FROM rooms WHERE status IN ('свободен', 'уборка', 'ремонт') ORDER BY room_number")
        rooms = cur.fetchall()
        setattr(self, f"room_{task_type}_data", rooms)
        combo_room['values'] = [f"{r['room_number']}" for r in rooms]
        if rooms: combo_room.current(0)
        position = 'уборщик' if task_type == "уборка" else 'ремонтник'
        cur.execute("SELECT staff_id, first_name, last_name FROM staff WHERE position=?", (position,))
        staff = cur.fetchall()
        setattr(self, f"staff_{task_type}_data", staff)
        combo_staff['values'] = [f"{s['first_name']} {s['last_name']}" for s in staff]
        if staff: combo_staff.current(0)
        conn.close()

    def assign_task(self, task_type):
        combo_room = self.combo_room_clean if task_type == "уборка" else self.combo_room_maint
        combo_staff = self.combo_staff_clean if task_type == "уборка" else self.combo_staff_maint
        r_idx = combo_room.current()
        s_idx = combo_staff.current()
        if r_idx < 0 or s_idx < 0:
            messagebox.showwarning("Внимание", "Выберите номер и сотрудника")
            return
        room_id = getattr(self, f"room_{task_type}_data")[r_idx]['room_id']
        staff_id = getattr(self, f"staff_{task_type}_data")[s_idx]['staff_id']
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT status FROM rooms WHERE room_id=?", (room_id,))
        room_status = cur.fetchone()['status']
        if room_status == 'занят':
            messagebox.showwarning("Внимание", "Нельзя назначить задачу занятому номеру. Сначала выселите гостя.")
            conn.close()
            return
        
        cur.execute("SELECT task_id FROM room_tasks WHERE room_id=? AND task_type=? AND status='ожидает' LIMIT 1", (room_id, task_type))
        if cur.fetchone():
            messagebox.showwarning("Внимание", f"Для этого номера уже есть активная задача: {task_type}.")
            conn.close()
            return

        cur.execute("INSERT INTO room_tasks (room_id, staff_id, task_type) VALUES (?, ?, ?)", (room_id, staff_id, task_type))
        cur.execute("UPDATE rooms SET status=? WHERE room_id=?", (task_type, room_id))
        conn.commit()
        conn.close()
        if task_type == "уборка": self.show_cleaning()
        else: self.show_maintenance()

    def render_tasks_tree(self, task_type):
        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("ID", "Номер", "Сотрудник", "Дата", "Статус")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ct.task_id, r.room_number, s.first_name || ' ' || s.last_name as staff_name, ct.task_date, ct.status
            FROM room_tasks ct
            JOIN rooms r ON ct.room_id = r.room_id
            JOIN staff s ON ct.staff_id = s.staff_id
            WHERE ct.task_type=? AND ct.status != 'завершено'
            ORDER BY ct.task_date DESC
        """, (task_type,))
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            tree.insert("", tk.END, values=(row['task_id'], row['room_number'], row['staff_name'], row['task_date'], row['status']))
        btn_complete = tk.Button(self.content_frame, text="Завершить выбранную", command=lambda: self.complete_task(task_type, tree), bg="#27ae60", fg="white")
        btn_complete.pack(pady=10)

    def complete_task(self, task_type, tree):
        selected = tree.selection()
        if not selected: return
        task_id = tree.item(selected[0], 'values')[0]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT room_id FROM room_tasks WHERE task_id=?", (task_id,))
        res = cur.fetchone()
        if res:
            cur.execute("UPDATE room_tasks SET status='завершено' WHERE task_id=?", (task_id,))
            cur.execute("SELECT status FROM rooms WHERE room_id=?", (res['room_id'],))
            if cur.fetchone()['status'] != 'занят':
                cur.execute("UPDATE rooms SET status='свободен' WHERE room_id=?", (res['room_id'],))
            conn.commit()
        conn.close()
        if task_type == "уборка": self.show_cleaning()
        else: self.show_maintenance()

    def show_stays(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Проживания и выселение", font=("Arial", 18, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("ID", "Гость", "Номер", "Заезд", "Выезд", "Сумма", "Оплата")
        self.stays_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.stays_tree.heading(col, text=col)
            if col == "Гость": self.stays_tree.column(col, width=180)
            else: self.stays_tree.column(col, width=120)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.stays_tree.yview)
        self.stays_tree.configure(yscroll=scrollbar.set)
        self.stays_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        btn_checkout = tk.Button(self.content_frame, text="Выселить гостя", command=self.checkout_guest, bg="#e74c3c", fg="white", font=("Arial", 10, "bold"))
        btn_checkout.pack(pady=10)
        self.load_stays_data()

    def load_stays_data(self):
        for i in self.stays_tree.get_children():
            self.stays_tree.delete(i)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""SELECT s.stay_id, g.first_name || ' ' || g.last_name as guest_name, r.room_number, s.check_in_date, s.check_out_date, s.total_price, s.payment_status FROM stays s JOIN guests g ON s.guest_id = g.guest_id JOIN rooms r ON s.room_id = r.room_id ORDER BY s.stay_id DESC""")
        rows = cur.fetchall()
        conn.close()
        for row in rows:
            self.stays_tree.insert("", tk.END, values=(row['stay_id'], row['guest_name'], row['room_number'], row['check_in_date'], row['check_out_date'], f"{row['total_price']} руб.", row['payment_status']))

    def checkout_guest(self):
        selected = self.stays_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите проживание для выселения")
            return
        item_values = self.stays_tree.item(selected[0], 'values')
        stay_id = int(item_values[0])
        room_number = item_values[2]
        resp = messagebox.askyesno("Подтверждение выселения", f"Выселить гостя из номера {room_number}?\nЗапись о проживании будет удалена. Выручка сохранится в истории гостя.")
        if resp:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT guest_id, room_id, total_price FROM stays WHERE stay_id=?", (stay_id,))
            res = cur.fetchone()
            if res:
                cur.execute("UPDATE guests SET total_spent = COALESCE(total_spent, 0) + ? WHERE guest_id=?", (res['total_price'], res['guest_id']))
                cur.execute("UPDATE rooms SET status='уборка' WHERE room_id=? AND status='занят'", (res['room_id'],))
                cur.execute("DELETE FROM stays WHERE stay_id=?", (stay_id,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Успех", f"Гость выселен. Выручка {item_values[5]} сохранена в профиле гостя.")
            self.load_stays_data()

    def show_guests(self):
        self.clear_content()
        tk.Label(self.content_frame, text="База гостей", font=("Arial", 18, "bold"), bg="white").pack(pady=20, anchor="w", padx=20)
        search_frame = tk.Frame(self.content_frame, bg="white")
        search_frame.pack(fill="x", padx=20)
        tk.Label(search_frame, text="Поиск по фамилии:", bg="white").pack(side="left")
        ent_search = tk.Entry(search_frame, width=30)
        ent_search.pack(side="left", padx=5)
        tree_frame = tk.Frame(self.content_frame)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        columns = ("ID", "Фамилия", "Имя", "Телефон", "Email", "Потрачено")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        def search_guests(event=None):
            for i in tree.get_children(): tree.delete(i)
            term = ent_search.get()
            conn = get_connection()
            cur = conn.cursor()
            if term: cur.execute("SELECT * FROM guests WHERE last_name LIKE ?", (f"%{term}%",))
            else: cur.execute("SELECT * FROM guests ORDER BY last_name")
            rows = cur.fetchall()
            conn.close()
            for row in rows:
                tree.insert("", tk.END, values=(row['guest_id'], row['last_name'], row['first_name'], row['phone'], row['email'], f"{row['total_spent']:.2f} руб."))
        ent_search.bind("<KeyRelease>", search_guests)
        search_guests()

if __name__ == "__main__":
    app = App()
    app.mainloop()
