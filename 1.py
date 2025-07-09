# LifeCode - Evolutionary Cellular Automata Sandbox (Improved Cell Visibility)

import raylibpy as rl
import numpy as np
import random
import math

# Constants
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 50
CELL_SIZE = WIDTH // GRID_SIZE
FPS = 10

# Global DNA (set by user at launch)
DNA = "B3/S23|M0.01"

# Grids
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
nutrient_map = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
history_map = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

wave_phase = 0.0

def parse_dna(dna_string):
    b_part, rest = dna_string.split("/")
    s_part, m_part = rest.split("|")
    birth = [int(n) for n in b_part[1:]]
    survive = [int(n) for n in s_part[1:]]
    mutation = float(m_part[1:])
    return birth, survive, mutation

def randomize_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            grid[y][x] = 1 if random.random() < 0.2 else 0
            history_map[y][x] = 0

def generate_nutrient_map():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            nutrient_map[y][x] = random.random()

def animate_nutrients():
    global wave_phase
    wave_phase += 0.05
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            wave = 0.5 + 0.5 * math.sin(wave_phase + x * 0.1 + y * 0.1)
            base = nutrient_map[y][x]
            nutrient_map[y][x] = max(0.0, min(1.0, 0.7 * base + 0.3 * wave))

def mutate_rule(birth, survive, mutation_rate):
    def maybe_flip(ruleset):
        rules = set(ruleset)
        if random.random() < mutation_rate:
            op = random.choice(["add", "remove"])
            val = random.randint(0, 8)
            if op == "add":
                rules.add(val)
            elif op == "remove" and val in rules:
                rules.remove(val)
        return sorted(rules)
    return maybe_flip(birth), maybe_flip(survive)

def count_neighbors(x, y):
    total = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % GRID_SIZE, (y + dy) % GRID_SIZE
            total += grid[ny][nx]
    return total

def update_grid(birth, survive, mutation):
    global grid
    new_grid = np.zeros_like(grid)
    b_mut, s_mut = mutate_rule(birth, survive, mutation)

    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            neighbors = count_neighbors(x, y)
            nutrient_bonus = nutrient_map[y][x]

            if grid[y][x] == 1:
                survives = neighbors in s_mut or (nutrient_bonus > 0.9)
                new_grid[y][x] = 1 if survives else 0
            else:
                born = neighbors in b_mut and (nutrient_bonus > 0.1)
                new_grid[y][x] = 1 if born else 0

            if new_grid[y][x] == 1:
                history_map[y][x] = min(history_map[y][x] + 1, 255)
            else:
                history_map[y][x] = max(history_map[y][x] - 1, 0)

    grid = new_grid

def draw_grid():
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            nutrient = nutrient_map[y][x]
            trail = history_map[y][x]

            # Background coloring (cool tones)
            r = int(40 + 60 * nutrient)
            g = int(140 + 40 * nutrient)
            b = int(230 - 80 * nutrient)
            background_color = rl.Color(r, g, b, 255)

            if grid[y][x]:
                rl.draw_rectangle(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1, rl.Color(0, 0, 0, 255))
            elif trail > 0:
                faded = rl.Color(0, 180, 0, min(trail, 255))
                rl.draw_rectangle(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1, faded)
            else:
                rl.draw_rectangle(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1, background_color)

def dna_input_gui():
    print("Enter DNA rule set in format B3/S23|M0.01:")
    user_input = input("DNA> ")
    return user_input if user_input else DNA

def main():
    global DNA
    DNA = dna_input_gui()
    birth, survive, mutation = parse_dna(DNA)

    rl.init_window(WIDTH, HEIGHT, b"LifeCode - Cellular Evolution")
    rl.set_target_fps(FPS)
    randomize_grid()
    generate_nutrient_map()

    paused = False

    while not rl.window_should_close():
        if rl.is_key_pressed(rl.KEY_SPACE):
            paused = not paused
        if rl.is_key_pressed(rl.KEY_R):
            randomize_grid()
            generate_nutrient_map()
        if rl.is_key_pressed(rl.KEY_D):
            DNA = dna_input_gui()
            birth, survive, mutation = parse_dna(DNA)

        animate_nutrients()

        if not paused:
            update_grid(birth, survive, mutation)

        rl.begin_drawing()
        rl.clear_background(rl.RAYWHITE)
        draw_grid()
        rl.draw_text(f"DNA: {DNA}  [SPACE] Pause  [R] Reset  [D] Edit DNA", 10, 10, 20, rl.DARKGRAY)
        rl.end_drawing()

    rl.close_window()

if __name__ == "__main__":
    main()
    