import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime


# ============= МОДУЛЬ 1: СОЗДАНИЕ БАЗЫ ДАННЫХ =============
def create_database():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()

    # Таблица фильмов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS films (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            year INTEGER,
            genre TEXT,
            duration INTEGER,
            actors TEXT,
            country TEXT,
            rating REAL,
            poster_url TEXT
        )
    ''')

    # Таблица залов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS halls (
            id INTEGER PRIMARY KEY,
            seats_count INTEGER
        )
    ''')

    # Таблица сеансов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            film_id INTEGER,
            time TEXT,
            date TEXT,
            hall_id INTEGER,
            price INTEGER,
            FOREIGN KEY (film_id) REFERENCES films(id),
            FOREIGN KEY (hall_id) REFERENCES halls(id)
        )
    ''')

    # Таблица заказов (билетов)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            seat_number INTEGER,
            purchase_datetime TEXT,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''')

    # Заполнение данных
    # Фильмы
    films_data = [
        (1, '12 Стульев', 1971, 'преступление, приключения, комедия', 153,
         'Арчил Гомеашвили, Сергей Филиппов, Михаил Пуговкин', 'СССР', 8.3, ''),
        (2, 'В бой идут одни старики', 1973, 'военный, драма, комедия', 87,
         'Леонид Быков, Сергей Подгорный, Рустам Сагдуллаев', 'СССР', 8.7, ''),
        (3, 'Брат', 1997, 'драма, преступление, боевик', 96, 'Сергей Бодров, Светлана Письмиченко, Виктор Сухоруков',
         'Россия', 8.4, ''),
        (4, 'Побег из Шоушенка', 1994, 'драма', 142, 'Тим Роббинс, Морган Фриман, Боб Гантон', 'США', 9.1, ''),
        (5, 'Король и Шут. Навсегда', 2026, 'фэнтези, комедия, драма', 118,
         'Константин Плотников, Влад Коноплёв, Дарья Мельникова', 'Россия', 6.8, ''),
        (6, 'Интерстеллар', 2014, 'фантастика, драма', 169, 'Мэттью Макконахи, Энн Хэтэуэй, Джессика Честейн', 'США',
         8.7, ''),
        (7, 'Властелин колец: Братство кольца', 2001, 'фэнтези, приключения, драма', 178,
         'Элайджа Вуд, Иэн Маккеллен, Шон Эстин', 'Новая Зеландия', 8.6, '')
    ]

    for film in films_data:
        cursor.execute(
            'INSERT OR IGNORE INTO films (id, name, year, genre, duration, actors, country, rating, poster_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
            film)

    # Залы
    halls_data = [(1, 30), (2, 40), (3, 25), (4, 30), (5, 35)]
    for hall in halls_data:
        cursor.execute('INSERT OR IGNORE INTO halls (id, seats_count) VALUES (?, ?)', hall)

    # Сеансы
    sessions_data = [
        (1, 1, '13:30', '2026-05-15', 2, 300),
        (2, 7, '17:15', '2026-05-16', 3, 700),
        (3, 6, '21:15', '2026-05-16', 3, 600),
        (4, 5, '14:45', '2026-05-18', 4, 450),
        (5, 3, '12:30', '2026-05-15', 1, 350)
    ]

    for session in sessions_data:
        cursor.execute(
            'INSERT OR IGNORE INTO sessions (id, film_id, time, date, hall_id, price) VALUES (?, ?, ?, ?, ?, ?)',
            session)

    # Заказы (уже купленные места)
    orders_data = [
        (1, 5, 4, '2026-05-13 23:23:00'),
        (2, 2, 20, '2026-05-10 12:31:00'),
        (3, 1, 14, '2026-05-15 10:00:00'),
        (4, 4, 21, '2026-05-17 23:59:00')
    ]

    for order in orders_data:
        cursor.execute(
            'INSERT OR IGNORE INTO orders (id, session_id, seat_number, purchase_datetime) VALUES (?, ?, ?, ?)', order)

    conn.commit()
    conn.close()


# ============= МОДУЛЬ 3: ЗАПРОС (Российские фильмы 15.05.2026) =============
def get_russian_sessions_15052026():
    conn = sqlite3.connect('cinema.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT f.name, s.time, s.date, h.seats_count, s.price
        FROM sessions s
        JOIN films f ON s.film_id = f.id
        JOIN halls h ON s.hall_id = h.id
        WHERE f.country = 'Россия' AND s.date = '2026-05-15'
    ''')
    results = cursor.fetchall()
    conn.close()
    return results


# ============= ГЛАВНОЕ ОКНО (МОДУЛЬ 4) =============
class CinemaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Кинотеатр - Покупка билетов")
        self.root.geometry("800x600")

        # Заголовок
        title_label = tk.Label(root, text="🍿 КИНОТЕАТР 🎬", font=("Arial", 20, "bold"), fg="darkred")
        title_label.pack(pady=10)

        # Создаем canvas для скролла
        canvas = tk.Canvas(root)
        scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_films()

    def load_films(self):
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, year, country, actors, rating FROM films")
        films = cursor.fetchall()
        conn.close()

        for film in films:
            self.create_film_card(film)

    def create_film_card(self, film):
        frame = tk.Frame(self.scrollable_frame, bd=2, relief="groove", padx=10, pady=10)
        frame.pack(fill="x", padx=10, pady=5)

        # Постер (заглушка - текстовая рамка)
        poster_frame = tk.Frame(frame, width=150, height=200, bg="gray", relief="solid", bd=1)
        poster_frame.grid(row=0, column=0, rowspan=4, padx=10, pady=5)
        poster_frame.grid_propagate(False)
        poster_label = tk.Label(poster_frame, text="🎬\nПОСТЕР", font=("Arial", 12), bg="gray", fg="white")
        poster_label.pack(expand=True)

        # Информация о фильме
        info_text = f"Название: {film[1]}\nСтрана: {film[3]}\nГод: {film[2]}\nАктеры: {film[4][:50]}..."
        info_label = tk.Label(frame, text=info_text, justify="left", font=("Arial", 10))
        info_label.grid(row=0, column=1, sticky="w", padx=10)

        # Оценка
        rating_label = tk.Label(frame, text=f"⭐ Оценка: {film[5]}", font=("Arial", 12, "bold"), fg="gold")
        rating_label.grid(row=1, column=1, sticky="w", padx=10)

        # Кнопка "Купить билет"
        buy_btn = tk.Button(frame, text="🎫 Купить билет", command=lambda f=film: self.open_session_window(f),
                            bg="lightblue", font=("Arial", 10))
        buy_btn.grid(row=2, column=1, sticky="w", padx=10, pady=10)

    def open_session_window(self, film):
        SessionWindow(self.root, film)


# ============= ОКНО ВЫБОРА СЕАНСА (МОДУЛЬ 5) =============
class SessionWindow:
    def __init__(self, parent, film):
        self.parent = parent
        self.film = film
        self.window = tk.Toplevel(parent)
        self.window.title(f"Выбор сеанса - {film[1]}")
        self.window.geometry("600x400")

        tk.Label(self.window, text=f"Фильм: {film[1]}", font=("Arial", 16, "bold")).pack(pady=10)

        # Загружаем сеансы для этого фильма
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id, s.date, s.time, s.price, h.seats_count
            FROM sessions s
            JOIN halls h ON s.hall_id = h.id
            WHERE s.film_id = ?
        ''', (film[0],))
        self.sessions = cursor.fetchall()
        conn.close()

        if not self.sessions:
            tk.Label(self.window, text="Нет доступных сеансов", font=("Arial", 12), fg="red").pack(pady=20)
            return

        for session in self.sessions:
            frame = tk.Frame(self.window, bd=1, relief="solid", padx=10, pady=10)
            frame.pack(fill="x", padx=20, pady=5)

            info_text = f"📅 Дата: {session[1]} | ⏰ Время: {session[2]} | 💰 Цена: {session[3]} руб. | 🪑 Мест в зале: {session[4]}"
            tk.Label(frame, text=info_text, font=("Arial", 10)).pack(side="left", padx=10)

            btn = tk.Button(frame, text="Выбрать место", command=lambda s=session: self.open_seat_selection(s),
                            bg="green", fg="white")
            btn.pack(side="right")

    def open_seat_selection(self, session):
        self.window.destroy()
        SeatSelectionWindow(self.parent, self.film, session)


# ============= ОКНО ВЫБОРА МЕСТА =============
class SeatSelectionWindow:
    def __init__(self, parent, film, session):
        self.parent = parent
        self.film = film
        self.session = session
        self.selected_seats = []

        self.window = tk.Toplevel(parent)
        self.window.title(f"Выбор места - {film[1]}")
        self.window.geometry("650x600")

        # Информация о сеансе
        info_frame = tk.Frame(self.window, bg="lightyellow", padx=10, pady=10)
        info_frame.pack(fill="x", padx=20, pady=10)

        info_text = f"Фильм: {film[1]}\nДата: {session[1]} | Время: {session[2]} | Цена за билет: {session[3]} руб."
        tk.Label(info_frame, text=info_text, font=("Arial", 11), justify="left").pack()

        # Получаем занятые места
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        cursor.execute("SELECT seat_number FROM orders WHERE session_id = ?", (session[0],))
        self.booked_seats = [row[0] for row in cursor.fetchall()]
        conn.close()

        # ЭКРАН
        screen_frame = tk.Frame(self.window, bg="black", height=60)
        screen_frame.pack(fill="x", padx=40, pady=10)
        tk.Label(screen_frame, text="ЭКРАН", fg="white", bg="black", font=("Arial", 14, "bold")).pack(expand=True)

        # Сетка мест
        seats_frame = tk.Frame(self.window)
        seats_frame.pack(pady=20)

        self.seat_buttons = {}
        seats_per_row = 8
        rows = (self.session[4] + seats_per_row - 1) // seats_per_row

        for i in range(1, self.session[4] + 1):
            row = (i - 1) // seats_per_row
            col = (i - 1) % seats_per_row

            if i in self.booked_seats:
                btn = tk.Button(seats_frame, text=str(i), width=4, height=1,
                                bg="red", state="disabled", font=("Arial", 9))
            else:
                btn = tk.Button(seats_frame, text=str(i), width=4, height=1,
                                bg="lightgreen", command=lambda seat=i: self.toggle_seat(seat),
                                font=("Arial", 9))

            btn.grid(row=row, column=col, padx=2, pady=2)
            self.seat_buttons[i] = btn

        # Легенда
        legend_frame = tk.Frame(self.window)
        legend_frame.pack(pady=10)
        tk.Label(legend_frame, text="🟢 Свободно", fg="green").pack(side="left", padx=10)
        tk.Label(legend_frame, text="🟡 Выбрано", fg="orange").pack(side="left", padx=10)
        tk.Label(legend_frame, text="🔴 Занято", fg="red").pack(side="left", padx=10)

        # Сумма
        self.total_label = tk.Label(self.window, text="Сумма: 0 руб.", font=("Arial", 14, "bold"), fg="blue")
        self.total_label.pack(pady=10)

        # Кнопка оплаты
        tk.Button(self.window, text="💳 Оплатить", command=self.pay,
                  bg="darkblue", fg="white", font=("Arial", 12, "bold"),
                  padx=30, pady=10).pack(pady=10)

    def toggle_seat(self, seat):
        if seat in self.selected_seats:
            self.selected_seats.remove(seat)
            self.seat_buttons[seat].config(bg="lightgreen")
        else:
            self.selected_seats.append(seat)
            self.seat_buttons[seat].config(bg="yellow")

        total = len(self.selected_seats) * self.session[3]
        self.total_label.config(text=f"Сумма: {total} руб.")

    def pay(self):
        if not self.selected_seats:
            messagebox.showwarning("Ошибка", "Выберите хотя бы одно место!")
            return

        # Подтверждение
        answer = messagebox.askyesno("Подтверждение",
                                     f"Вы выбрали {len(self.selected_seats)} мест(о) на сумму {len(self.selected_seats) * self.session[3]} руб.\nПодтверждаете покупку?")

        if not answer:
            return

        # Сохраняем заказы
        conn = sqlite3.connect('cinema.db')
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for seat in self.selected_seats:
            cursor.execute('''
                INSERT INTO orders (session_id, seat_number, purchase_datetime)
                VALUES (?, ?, ?)
            ''', (self.session[0], seat, now))

        conn.commit()
        conn.close()

        # Показываем чек
        self.show_check()

    def show_check(self):
        check_window = tk.Toplevel(self.window)
        check_window.title("Чек - Билет")
        check_window.geometry("500x550")
        check_window.configure(bg="white")

        # Рамка чека
        check_frame = tk.Frame(check_window, bg="white", bd=2, relief="solid")
        check_frame.pack(fill="both", expand=True, padx=20, pady=20)

        check_text = f"""
╔════════════════════════════════════════╗
║                                        ║
║         🎬 БИЛЕТ В КИНО 🎬             ║
║                                        ║
╠════════════════════════════════════════╣
║                                        ║
║  Фильм: {self.film[1]}                        
║                                        ║
║  Дата: {self.session[1]}                          
║                                        ║
║  Время: {self.session[2]}                         
║                                        ║
║  Зал: {self.session[4]}                             
║                                        ║
║  Места: {', '.join(map(str, self.selected_seats))}                  
║                                        ║
║  Количество билетов: {len(self.selected_seats)}                    
║                                        ║
║  Цена: {len(self.selected_seats) * self.session[3]} руб.                  
║                                        ║
╠════════════════════════════════════════╣
║                                        ║
║      ПРИЯТНОГО ПРОСМОТРА! 🍿           ║
║                                        ║
╚════════════════════════════════════════╝
        """

        tk.Label(check_frame, text=check_text, font=("Courier", 10),
                 justify="left", bg="white").pack(padx=20, pady=20)

        tk.Button(check_frame, text="Закрыть", command=lambda: self.close_all(check_window),
                  bg="gray", font=("Arial", 10), padx=20).pack(pady=10)

    def close_all(self, check_window):
        check_window.destroy()
        self.window.destroy()
        messagebox.showinfo("Спасибо!", "Билет успешно куплен! Приятного просмотра!")


# ============= ЗАПУСК =============
if __name__ == "__main__":
    # Создаем базу данных
    create_database()

    # МОДУЛЬ 3: Выполняем запрос и выводим в консоль
    print("=" * 50)
    print("МОДУЛЬ 3: Российские фильмы на 15.05.2026")
    print("=" * 50)
    russian_sessions = get_russian_sessions_15052026()
    if russian_sessions:
        for session in russian_sessions:
            print(
                f"Фильм: {session[0]}, Время: {session[1]}, Дата: {session[2]}, Мест в зале: {session[3]}, Цена: {session[4]} руб.")
    else:
        print("Нет российских фильмов на 15.05.2026")
    print("=" * 50)
    print()

    # Запуск GUI
    root = tk.Tk()
    app = CinemaApp(root)
    root.mainloop()
