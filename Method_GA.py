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
    {"name": "Водитель 1", "break_type": "big"},
    {"name": "Водитель 2", "break_type": "big"},
    {"name": "Водитель 3", "break_type": "big"},
    {"name": "Водитель 4", "break_type": "big"},
    {"name": "Водитель 5", "break_type": "small"},
    {"name": "Водитель 6", "break_type": "small"},
    {"name": "Водитель 7", "break_type": "small"},
    {"name": "Водитель 8", "break_type": "small"},
]

routes = [1, 2]

# проверка часов в час пик
def is_peak(hour):
    for (s, e) in PEAK_HOURS:
        if s <= hour < e:
            return True
    return False

# возвращение списка часов в смене
def get_shift_hours(start, duration):
    return [(start + i) % 24 for i in range(duration)]


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

# создание расписание для одного водителя
def create_driver_schedule(driver):

    schedule = {}
    shift_start = random.randint(6, 18)  
    shift_hours = get_shift_hours(shift_start, SHIFT_DURATION)
    shift_end = (shift_start + SHIFT_DURATION) % 24

    breaks = assign_breaks(shift_hours, driver['break_type'])

    route = 1

    for i, hour in enumerate(shift_hours):
        if hour == shift_start:
            if is_peak(hour):
                schedule[hour] = f'Начало смены (час пик) + Поездка Маршрут: №{route}'
            else:
                schedule[hour] = f'Начало смены + Поездка Маршрут: №{route}'
            route = 2 if route == 1 else 1 
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

# генерация начальной популяции
def generate_initial_population():
    population = []
    for _ in range(POPULATION_SIZE):
        individual = {}
        for driver in drivers:
            schedule = create_driver_schedule(driver)
            individual[driver['name']] = schedule
        population.append(individual)
    return population

# фитнес-оценка
def fitness(individual):
    score = 0
    peak_coverage = {7:0, 8:0, 17:0, 18:0}

    for driver in drivers:
        schedule = individual[driver['name']]
        activities = list(schedule.values())
        if any('Начало смены' in act for act in activities):
            score += 1
        if any('Окончание смены' in act for act in activities):
            score += 1
        if driver['break_type'] == 'big':
            num_breaks = activities.count('Большой перерыв')
            if num_breaks == 1:
                score += 2
        elif driver['break_type'] == 'small':
            num_breaks = activities.count('Короткий перерыв')
            if num_breaks == 2:
                score += 2
        trips = [act for act in activities if act.startswith('Поездка')]
        score += len(trips)
        for peak_hour in peak_coverage.keys():
            if individual[driver['name']].get(peak_hour, '').startswith('Поездка'):
                peak_coverage[peak_hour] += 1
    for peak_hour, count in peak_coverage.items():
        if count >= 2:  
            score += 3
        elif count == 1:
            score += 1
    return score

# селекция
def selection(population):
    sorted_population = sorted(population, key=lambda x: fitness(x), reverse=True)
    return sorted_population[:int(POPULATION_SIZE * 0.2)]  # топ 20%

# кроссовинговер
def crossover(parent1, parent2):
    child = {}
    for driver in drivers:
        if random.random() < 0.5:
            child[driver['name']] = copy.deepcopy(parent1[driver['name']])
        else:
            child[driver['name']] = copy.deepcopy(parent2[driver['name']])
    return child

# мутация
def mutate(individual):
    for driver in drivers:
        if random.random() < MUTATION_RATE:
            individual[driver['name']] = create_driver_schedule(driver)
    return individual

# основная функция ГА
def genetic_algorithm():
    population = generate_initial_population()
    best_fitness = 0
    best_individual = None
    for generation in range(GENERATIONS):
        # оценка фитнеса
        population_fitness = [(fitness(individual), individual) for individual in population]
        population_fitness.sort(key=lambda x: x[0], reverse=True)
        if population_fitness[0][0] > best_fitness:
            best_fitness = population_fitness[0][0]
            best_individual = population_fitness[0][1]
            print(f"Поколение {generation}: Лучший фитнес = {best_fitness}")
        # селекция
        parents = selection(population)
        # кроссовинговер и мутация
        next_generation = parents.copy()
        while len(next_generation) < POPULATION_SIZE:
            parent1, parent2 = random.sample(parents, 2)
            child = crossover(parent1, parent2)
            child = mutate(child)
            next_generation.append(child)
        population = next_generation
    return best_individual

# создание интерфейса 
def create_gui():
    root = tk.Tk()
    root.title("Генетический Алгоритм Расписания Водителей")
    root.geometry("1200x700")  
    root.configure(bg="#f0f0f0")

    header = tk.Label(root, text="Оптимизация Расписания Водителей Автобусов с Помощью Генетического Алгоритма",
                      font=("Helvetica", 16, "bold"), bg="#f0f0f0")
    header.pack(pady=10)

    # кнопка запуска алгоритма
    run_button = ttk.Button(root, text="Запустить Оптимизацию", command=lambda: run_genetic_algorithm(root))
    run_button.pack(pady=10)

    # создание холста с прокруткой
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

    hours = list(range(6, 24)) + list(range(0, 4))  
    hour_labels = [f"{h:02d}:00" for h in hours]

    for col, hour in enumerate(hour_labels):
        lbl = ttk.Label(table_frame, text=hour, borderwidth=2, relief="groove", width=15, anchor='center',
                       background="#d3d3d3", font=("Helvetica", 12, "bold"))
        lbl.grid(row=0, column=col + 1, sticky='nsew', padx=1, pady=1)

    for row, driver in enumerate(drivers, start=1):
        name = driver['name']
        lbl = ttk.Label(table_frame, text=name, borderwidth=2, relief="groove", width=25, anchor='center',
                       background="#f0f0f0", font=("Helvetica", 12, "bold"))
        lbl.grid(row=row, column=0, sticky='nsew', padx=1, pady=1)
        for col in range(len(hour_labels)):
            lbl_activity = tk.Label(table_frame, text='', borderwidth=1, relief="solid", width=15,
                                    anchor='center', background='#FFFFFF', font=("Helvetica", 12))
            lbl_activity.grid(row=row, column=col + 1, sticky='nsew', padx=1, pady=1)

    # добавление легенды под таблицей
    legend_frame = ttk.Frame(root)
    legend_frame.pack(pady=20)

    legends = {
        'Начало смены (час пик)': '#FF6347',
        'Начало смены + Поездка Маршрут: №1': '#8FBC8F',
        'Начало смены + Поездка Маршрут: №2': '#8FBC8F',
        'Окончание смены': '#8FBC8F',
        'Поездка Маршрут: №1': '#ADD8E6',
        'Поездка Маршрут: №2': '#00008B',
        'Поездка (час пик)': '#FF6347',
        'Большой перерыв': '#FFD700',
        'Короткий перерыв': '#FFA500',
    }

    for i, (text, color) in enumerate(legends.items()):
        color_lbl = tk.Label(legend_frame, text='     ', bg=color, borderwidth=2, relief="solid")
        color_lbl.grid(row=0, column=i, padx=5, pady=5)
        text_lbl = ttk.Label(legend_frame, text=text, font=("Helvetica", 12))
        text_lbl.grid(row=1, column=i, padx=5, pady=5)

    root.mainloop()

# показ расписания
def display_schedule(schedule, table_frame, hour_labels):
    for widget in table_frame.winfo_children():
        info = widget.grid_info()
        if info['row'] != 0 and info['column'] != 0:
            widget.destroy()

    # заполнение таблицы новым расписанием
    for row, driver in enumerate(drivers, start=1):
        for col, hour in enumerate(hour_labels):
            hour_num = int(hour.split(':')[0])
            activity = schedule.get(driver['name'], {}).get(hour_num, '')

            if activity == 'Начало смены (час пик) + Поездка Маршрут: №1':
                bg_color = '#FF6347'  
            elif activity == 'Начало смены (час пик) + Поездка Маршрут: №2':
                bg_color = '#FF6347'  
            elif activity.startswith('Начало смены + Поездка Маршрут:'):
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

    table_frame.update()

# запуск ГА и отображение таблицы
def run_genetic_algorithm(root):
    for widget in root.winfo_children():
        if isinstance(widget, ttk.Button):
            widget.config(state='disabled')

    messagebox.showinfo("Генетический Алгоритм", "Запуск генетического алгоритма. Пожалуйста, подождите...")
    best_schedule = genetic_algorithm()
    messagebox.showinfo("Генетический Алгоритм", "Оптимизация завершена!")

    canvas = root.pack_slaves()[2]  
    table_frame = canvas.winfo_children()[0]

    hours = list(range(6, 24)) + list(range(0, 4))
    hour_labels = [f"{h:02d}:00" for h in hours]

    display_schedule(best_schedule, table_frame, hour_labels)

    for widget in root.winfo_children():
        if isinstance(widget, ttk.Button):
            widget.config(state='normal')

def main():
    create_gui()

if __name__ == "__main__":
    main()
