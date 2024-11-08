import tkinter as tk
from tkinter import ttk
import random


def target_function(chromosome):
    x1, x2 = chromosome
    return (x2 - x1 ** 2) ** 2 + (1 - x1) ** 2

def tournament_selection(population, fitness, tournament_size):
    tournament_indices = random.sample(range(len(population)), tournament_size)
    tournament = [population[i] for i in tournament_indices]
    tournament_fitness = [fitness[i] for i in tournament_indices]
    best_index = tournament_fitness.index(min(tournament_fitness))
    return tournament[best_index]

def random_selection(population, fitness):
    return random.choice(population)

def crossover(parent1, parent2):
    child1 = [parent1[0], parent2[1]]
    child2 = [parent2[0], parent1[1]]
    return child1, child2

def mutate(chromosome, mutation_rate, gene_min, gene_max):
    return [gene if random.random() > mutation_rate else random.uniform(gene_min, gene_max) for gene in chromosome]

def genetic_algorithm(is_modified):
    params = get_parameters_from_ui()
    population = initialize_population(params)
    fitness = calculate_fitness(population)

    best_chromosome, best_fitness = None, float('inf')

    for generation in range(params['generations']):
        if is_modified:
            population, fitness = modified_generation(population, fitness, params)
        else:
            population, fitness = standard_generation(population, fitness, params)

        best_chromosome, best_fitness = update_best_solution(population, fitness, best_chromosome, best_fitness)

        update_gui(is_modified, generation, best_chromosome, best_fitness, population, fitness)


def get_parameters_from_ui():
    return {
        'mutation_rate': float(mutation_rate_entry.get()) / 100,
        'generations': int(generations_entry.get()),
        'chromosome_count': int(chromosome_count_entry.get()),
        'gene_min': float(gene_min_entry.get()),
        'gene_max': float(gene_max_entry.get()),
        'elite_count': max(1, int(chromosome_count_entry.get()) // 25)
    }


def initialize_population(params):
    return [[random.uniform(params['gene_min'], params['gene_max']) for _ in range(2)]
            for _ in range(params['chromosome_count'])]


def calculate_fitness(population):
    return [target_function(chromo) for chromo in population]


def modified_generation(population, fitness, params):
    sorted_population = sorted(zip(population, fitness), key=lambda x: x[1])
    elites = [chromo for chromo, _ in sorted_population[:params['elite_count']]]

    new_population = elites.copy()
    while len(new_population) < params['chromosome_count']:
        parent1 = tournament_selection(population, fitness, 3)
        parent2 = tournament_selection(population, fitness, 3)
        child1, child2 = crossover(parent1, parent2)
        new_population.extend([
            mutate(child1, params['mutation_rate'], params['gene_min'], params['gene_max']),
            mutate(child2, params['mutation_rate'], params['gene_min'], params['gene_max'])
        ])

    new_population = new_population[:params['chromosome_count']]
    new_fitness = calculate_fitness(new_population)
    return new_population, new_fitness


def standard_generation(population, fitness, params):
    new_population = []
    while len(new_population) < params['chromosome_count']:
        parent1 = random_selection(population, fitness)
        parent2 = random_selection(population, fitness)
        child1, child2 = crossover(parent1, parent2)
        new_population.extend([
            mutate(child1, params['mutation_rate'], params['gene_min'], params['gene_max']),
            mutate(child2, params['mutation_rate'], params['gene_min'], params['gene_max'])
        ])

    new_population = new_population[:params['chromosome_count']]
    new_fitness = calculate_fitness(new_population)
    return new_population, new_fitness


def update_best_solution(population, fitness, best_chromosome, best_fitness):
    current_best = min(fitness)
    if current_best < best_fitness:
        best_fitness = current_best
        best_chromosome = population[fitness.index(best_fitness)]
    return best_chromosome, best_fitness


def update_gui(is_modified, generation, best_chromosome, best_fitness, population, fitness):
    label_prefix = '' if is_modified else '_standard'
    globals()[f'generations_completed_label{label_prefix}'][
        'text'] = f"Количество прошлых поколений ({'модификация' if is_modified else 'обычный'}): {generation + 1}"
    globals()[f'best_solution_label{label_prefix}'][
        'text'] = f"X[1] = {best_chromosome[0]:.6f}, X[2] = {best_chromosome[1]:.6f}"
    globals()[f'function_value_label{label_prefix}']['text'] = f"{best_fitness:.6f}"

    for i in tree.get_children():
        tree.delete(i)
    for i, chromo in enumerate(population):
        tree.insert("", "end", values=(i + 1, fitness[i], chromo[0], chromo[1]))

    window.update()

def modified_genetic_algorithm():
    genetic_algorithm(is_modified=True)


def standard_genetic_algorithm():
    genetic_algorithm(is_modified=False)


window = tk.Tk()
window.title("Генетический алгоритм")
window.geometry("800x700")

params_frame = tk.Frame(window)
params_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

function_label = tk.Label(params_frame, text="Функция: (x2 - x1^2)^2 + (1 - x1)^2")
function_label.grid(row=0, column=0, columnspan=2, sticky="w")

tk.Label(params_frame, text="Вероятность мутации, %:").grid(row=1, column=0, sticky="w")
mutation_rate_entry = tk.Entry(params_frame)
mutation_rate_entry.insert(0, "50")
mutation_rate_entry.grid(row=1, column=1)

tk.Label(params_frame, text="Количество хромосом:").grid(row=2, column=0, sticky="w")
chromosome_count_entry = tk.Entry(params_frame)
chromosome_count_entry.insert(0, "50")
chromosome_count_entry.grid(row=2, column=1)

tk.Label(params_frame, text="Минимальное значение гена:").grid(row=3, column=0, sticky="w")
gene_min_entry = tk.Entry(params_frame)
gene_min_entry.insert(0, "-46")
gene_min_entry.grid(row=3, column=1)

tk.Label(params_frame, text="Максимальное значение гена:").grid(row=4, column=0, sticky="w")
gene_max_entry = tk.Entry(params_frame)
gene_max_entry.insert(0, "46")
gene_max_entry.grid(row=4, column=1)

tk.Label(params_frame, text="Количество поколений:").grid(row=5, column=0, sticky="w")
generations_entry = tk.Entry(params_frame)
generations_entry.insert(0, "100")
generations_entry.grid(row=5, column=1)

control_frame = tk.Frame(window)
control_frame.grid(row=1, column=0, padx=10, pady=10, sticky="n")

run_button_modified = tk.Button(control_frame, text="Рассчитать (модифицированный)", command=modified_genetic_algorithm)
run_button_modified.grid(row=0, column=0)

run_button_standard = tk.Button(control_frame, text="Рассчитать (обычный)", command=standard_genetic_algorithm)
run_button_standard.grid(row=0, column=1)

generations_completed_label = tk.Label(control_frame, text="Количество прошлых поколений (модификация): 0")
generations_completed_label.grid(row=1, column=0, columnspan=2)

generations_completed_label_standard = tk.Label(control_frame, text="Количество прошлых поколений (обычный): 0")
generations_completed_label_standard.grid(row=2, column=0, columnspan=2)

results_frame = tk.Frame(window)
results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="n")

tk.Label(results_frame, text="Лучшее решение (модификация):").grid(row=0, column=0, sticky="w")
best_solution_label = tk.Label(results_frame, text="")
best_solution_label.grid(row=1, column=0, sticky="w")

tk.Label(results_frame, text="Значение функции (модификация):").grid(row=2, column=0, sticky="w")
function_value_label = tk.Label(results_frame, text="")
function_value_label.grid(row=3, column=0, sticky="w")

tk.Label(results_frame, text="Лучшее решение (обычный):").grid(row=4, column=0, sticky="w")
best_solution_label_standard = tk.Label(results_frame, text="")
best_solution_label_standard.grid(row=5, column=0, sticky="w")

tk.Label(results_frame, text="Значение функции (обычный):").grid(row=6, column=0, sticky="w")
function_value_label_standard = tk.Label(results_frame, text="")
function_value_label_standard.grid(row=7, column=0, sticky="w")

table_frame = tk.Frame(window)
table_frame.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

tree = ttk.Treeview(table_frame, columns=("Номер", "Результат", "Ген 1", "Ген 2"), show="headings")
tree.heading("Номер", text="Номер")
tree.heading("Результат", text="Результат")
tree.heading("Ген 1", text="Ген 1")
tree.heading("Ген 2", text="Ген 2")
tree.pack(expand=True, fill="both")

window.mainloop()