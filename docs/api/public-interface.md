# Публичный интерфейс ядра

Ядро (`packages/core`) предоставляет функции для работы с данными отеля. Приложение (`app/ui`) вызывает эти функции для реализации пользовательского интерфейса.

## Работа с базой данных

### `get_connection()`
Возвращает соединение с SQLite. Включает поддержку внешних ключей.

**Возвращает:** `sqlite3.Connection`

### `init_db()`
Создаёт таблицы и заполняет начальные данные (категории, номера, персонал, услуги). Вызывается при запуске приложения.

---

## Работа с гостями

### `register_guest(first_name, last_name, phone, email)`
Регистрирует нового гостя.

**Параметры:**
- `first_name` (str) — имя
- `last_name` (str) — фамилия
- `phone` (str) — телефон
- `email` (str) — email

**Возвращает:** `int` — ID гостя

**Исключения:** `ValueError` — если имя или фамилия пустые

### `get_all_guests(search_term=None)`
Возвращает список гостей. Если указан `search_term`, фильтрует по фамилии.

**Параметры:**
- `search_term` (str, optional) — текст для поиска

**Возвращает:** `list[sqlite3.Row]`

---

## Работа с номерами

### `get_room_categories()`
Возвращает список категорий номеров с ценами.

**Возвращает:** `list[sqlite3.Row]` — каждая строка содержит `category_id`, `category_name`, `base_price`

### `get_available_room_by_category(category_id)`
Находит первый свободный номер указанной категории.

**Параметры:**
- `category_id` (int) — ID категории

**Возвращает:** `sqlite3.Row` или `None`

### `get_room_status(room_id)`
Возвращает текущий статус номера.

**Параметры:**
- `room_id` (int) — ID номера

**Возвращает:** `str` — статус (`available`, `occupied`, `cleaning`, `maintenance`)

### `update_room_status(room_id, status)`
Обновляет статус номера.

**Параметры:**
- `room_id` (int) — ID номера
- `status` (str) — новый статус

### `get_next_room_status(current_status)`
Возвращает следующий статус в цикле: `available` → `cleaning` → `maintenance` → `available`.

**Параметры:**
- `current_status` (str) — текущий статус

**Возвращает:** `str` — следующий статус

### `occupy_room(room_id)`
Устанавливает статус номера в `occupied`.

**Параметры:**
- `room_id` (int) — ID номера

---

## Работа с проживанием

### `calculate_stay_price(base_price, nights, services)`
Рассчитывает общую стоимость проживания.

**Параметры:**
- `base_price` (float) — цена номера за ночь
- `nights` (int) — количество ночей
- `services` (list[dict]) — список услуг, каждая с ключом `price`

**Возвращает:** `float` — общая стоимость

**Исключения:** `ValueError` — если `nights <= 0`

### `create_stay(guest_id, room_id, check_in, check_out, total_price)`
Создаёт запись о проживании.

**Параметры:**
- `guest_id` (int) — ID гостя
- `room_id` (int) — ID номера
- `check_in` (str) — дата заезда (YYYY-MM-DD)
- `check_out` (str) — дата выезда (YYYY-MM-DD)
- `total_price` (float) — стоимость

**Возвращает:** `int` — ID проживания

### `get_all_stays()`
Возвращает список всех проживаний с информацией о госте и номере.

**Возвращает:** `list[sqlite3.Row]`

### `checkout_guest(stay_id)`
Выселяет гостя: добавляет сумму к тратам гостя, меняет статус номера на `cleaning`, удаляет запись о проживании.

**Параметры:**
- `stay_id` (int) — ID проживания

---

## Работа с задачами

### `get_rooms_for_task(task_type)`
Возвращает список номеров, доступных для назначения задачи.

**Параметры:**
- `task_type` (str) — тип задачи (`cleaning` или `maintenance`)

**Возвращает:** `list[sqlite3.Row]`

### `get_staff_by_position(position)`
Возвращает список сотрудников указанной должности.

**Параметры:**
- `position` (str) — должность (`cleaner` или `maintenance_worker`)

**Возвращает:** `list[sqlite3.Row]`

### `assign_task(room_id, staff_id, task_type)`
Назначает задачу сотруднику для номера.

**Параметры:**
- `room_id` (int) — ID номера
- `staff_id` (int) — ID сотрудника
- `task_type` (str) — тип задачи

### `get_pending_tasks(task_type)`
Возвращает список незавершённых задач указанного типа.

**Параметры:**
- `task_type` (str) — тип задачи

**Возвращает:** `list[sqlite3.Row]`

### `complete_task(task_id)`
Завершает задачу и меняет статус номера на `available` (если номер не занят).

**Параметры:**
- `task_id` (int) — ID задачи

---

## Работа с услугами

### `get_services()`
Возвращает список доступных дополнительных услуг.

**Возвращает:** `list[sqlite3.Row]` — каждая строка содержит `service_id`, `service_name`, `price`

---

## Статистика

### `get_dashboard_stats()`
Возвращает статистику для дашборда.

**Возвращает:** `dict` с ключами:
- `total_rooms` (int) — всего номеров
- `occupied` (int) — занятых
- `available` (int) — свободных
- `revenue` (float) — общий доход
