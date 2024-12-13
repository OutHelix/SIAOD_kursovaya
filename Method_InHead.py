import tkinter as tk
from tkinter import ttk, messagebox
import random
import copy

# константы
PEAK_HOURS = [(7, 9), (17, 19)]  
SHIFT_DURATION = 9  
BREAK_DURATION_ONE = 1  
BREAK_DURATION_TWO = 0.25  
BREAK_INTERVAL = 3  
POPULATION_SIZE = 50
GENERATIONS = 100
MUTATION_RATE = 0.1

# список водителей
drivers = [
    {"name": "Водитель 1", "start": 6, "break_type": "big"},
    {"name": "Водитель 2", "start": 7, "break_type": "big"},
    {"name": "Водитель 3", "start": 8, "break_type": "big"},
    {"name": "Водитель 4", "start": 10, "break_type": "big"},
    {"name": "Водитель 5", "start": 11, "break_type": "small"},
    {"name": "Водитель 6", "start": 13, "break_type": "small"},
    {"name": "Водитель 7", "start": 16, "break_type": "small"},
    {"name": "Водитель 8", "start": 18, "break_type": "small"},
]

# час пики
def is_peak(hour):
    for (s, e) in PEAK_HOURS:
        if s <= hour < e:
            return True
    return False

# учитывание перерывов
def assign_breaks(shift_hours, break_type):
    breaks = []
    possible_breaks = [hour for hour in shift_hours if not is_peak(hour)]

    if break_type == "big":
        for i, hour in enumerate(shift_hours):
            if hour in possible_breaks and i >= 2:
                breaks.append(hour)
                break
    elif break_type == "small":
        first_break = None
        second_break = None
        for i, hour in enumerate(shift_hours):
            if hour in possible_breaks and i >= 2:
                if first_break is None:
                    first_break = hour
                elif (hour - first_break) % 24 >= BREAK_INTERVAL:
                    second_break = hour
                    break
        if first_break is not None:
            breaks.append(first_break)
        if second_break is not None:
            breaks.append(second_break)
    return breaks

# создание расписания для одного водителя
def create_driver_schedule(driver):
    schedule = {}
    shift_start = driver['start']
    shift_end = (shift_start + SHIFT_DURATION) % 24
    shift_hours = [(shift_start + i) % 24 for i in range(SHIFT_DURATION)]

    breaks = assign_breaks(shift_hours, driver['break_type'])

    route = 1

    for i, hour in enumerate(shift_hours):
        if hour == shift_start:
            if is_peak(hour):
                schedule[hour] = 'Начало смены (час пик)'
            else:
                schedule[hour] = 'Начало смены + Поездка Маршрут: №1'
                route = 2  
        elif hour in breaks:
            if driver['break_type'] == 'big':
                schedule[hour] = 'Большой перерыв'
            else:
                schedule[hour] = 'Короткий перерыв'
        else:
            if is_peak(hour):
                schedule[hour] = 'Поездка (час пик)'
            else:
                schedule[hour] = f'Поездка Маршрут: №{route}'
                route = 2 if route == 1 else 1  

    schedule[shift_end] = 'Окончание смены'

    return schedule

# генерация всего расписания
def generate_schedule():
    driver_schedules = {}
    for driver in drivers:
        schedule = create_driver_schedule(driver)
        driver_schedules[driver['name']] = schedule
    return driver_schedules

# создание интерфейса 
def create_gui(schedule):
    root = tk.Tk()
    root.title("Расписание Водителей Автобусов")
    root.geometry("1800x900")  
    root.configure(bg="#f0f0f0")

    header = tk.Label(root, text="Расписание Водителей Автобусов", font=("Helvetica", 20, "bold"), bg="#f0f0f0")
    header.pack(pady=20)

    canvas = tk.Canvas(root, bg="#f0f0f0")
    canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    v_scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    h_scrollbar = ttk.Scrollbar(root, orient="horizontal", command=canvas.xview)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # создание фрейма внутри холста
    table_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor='nw')

    # определение часов для столбцов
    hours = list(range(6, 24)) + list(range(0, 4))  
    hour_labels = [f"{h:02d}:00" for h in hours]

    for col, hour in enumerate(hour_labels):
        lbl = ttk.Label(table_frame, text=hour, borderwidth=2, relief="groove", width=15, anchor='center',
                       background="#d3d3d3", font=("Helvetica", 12, "bold"))
        lbl.grid(row=0, column=col + 1, sticky='nsew', padx=1, pady=1)

    for row, (driver, activities) in enumerate(schedule.items(), start=1):
        lbl = ttk.Label(table_frame, text=driver, borderwidth=2, relief="groove", width=25, anchor='center',
                       background="#f0f0f0", font=("Helvetica", 12, "bold"))
        lbl.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)

        for col, hour in enumerate(hour_labels):
            hour_num = int(hour.split(':')[0])
            activity = activities.get(hour_num, '')
            if activity == 'Начало смены (час пик)':
                bg_color = '#FF6347'  
            elif activity.startswith('Начало смены + Поездка'):
                bg_color = '#8FBC8F'  
            elif activity == 'Окончание смены':
                bg_color = '#8FBC8F'  
            elif activity.startswith('Поездка Маршрут: №1'):
                bg_color = '#ADD8E6'  
            elif activity.startswith('Поездка Маршрут: №2'):
                bg_color = '#00008B'  
            elif activity == 'Поездка (час пик)':
                bg_color = '#FF6347'  
            elif activity == 'Большой перерыв':
                bg_color = '#FFD700'  
            elif activity == 'Короткий перерыв':
                bg_color = '#FFA500'  
            else:
                bg_color = '#FFFFFF' 

            lbl_activity = tk.Label(table_frame, text=activity, borderwidth=1, relief="solid", width=15,
                                    anchor='center', background=bg_color, font=("Helvetica", 12))
            lbl_activity.grid(row=row, column=col + 1, sticky='nsew', padx=1, pady=1)

    for col in range(len(hour_labels) + 1):
        table_frame.columnconfigure(col, weight=1)
    for row in range(len(schedule) + 1):
        table_frame.rowconfigure(row, weight=1)

    # добавление легенды под таблицей
    legend_frame = ttk.Frame(root)
    legend_frame.pack(pady=20)

    legends = {
        'Начало смены (час пик)': '#FF6347',
        'Начало смены + Поездка Маршрут: №1': '#8FBC8F',
        'Окончание смены': '#8FBC8F',
        'Поездка Маршрут: №1': '#ADD8E6',
        'Поездка Маршрут: №2': '#00008B',
        'Поездка (час пик)': '#FF6347',
        'Большой перерыв': '#FFD700',
        'Короткий перерыв': '#FFA500',
    }

    for i, (text, color) in enumerate(legends.items()):
        color_lbl = tk.Label(legend_frame, text='     ', bg=color, borderwidth=2, relief="solid")
        color_lbl.grid(row=0, column=i, padx=10, pady=5)
        text_lbl = ttk.Label(legend_frame, text=text, font=("Helvetica", 12))
        text_lbl.grid(row=1, column=i, padx=10, pady=5)

    root.mainloop()

# запуск мейна
def main():
    schedule = generate_schedule()
    create_gui(schedule)

if __name__ == "__main__":
    main()
