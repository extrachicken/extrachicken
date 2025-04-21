# game_of_life.py
import random
import os
import time
import argparse

class Cell:
    """Представляет клетку в «Игре жизни» Конвея."""
    
    def __init__(self):
        """Инициализирует клетку в мертвом состоянии."""
        self.is_alive = False
        self.next_state = False
        
    def calculate_next_state(self, live_neighbors):
        """Вычисляет следующее состояние клетки по правилам игры.
        
        Args:
            live_neighbors (int): Количество живых соседей клетки.
        """
        if self.is_alive:
            # Живая клетка с менее чем 2 или более чем 3 живыми соседями умирает
            self.next_state = 2 <= live_neighbors <= 3
        else:
            # Мертвая клетка с ровно 3 живыми соседями оживает
            self.next_state = live_neighbors == 3
            
    def update(self):
        """Обновляет состояние клетки до ранее вычисленного следующего состояния."""
        self.is_alive = self.next_state
        self.next_state = False
        
    def __str__(self):
        """Возвращает строковое представление клетки."""
        return "●" if self.is_alive else "○"


class Grid:
    """Представляет сетку клеток для «Игры жизни»."""
    
    def __init__(self, width, height, random_init=False, seed_pattern=None):
        """Инициализирует сетку с указанными размерами.
        
        Args:
            width (int): Ширина сетки.
            height (int): Высота сетки.
            random_init (bool): Инициализировать ли случайными состояниями клеток.
            seed_pattern (list): Опционально, 2D-список, представляющий начальный паттерн.
        """
        self.width = width
        self.height = height
        self.grid = [[Cell() for _ in range(width)] for _ in range(height)]
        self.living_cells_count = 0  # Счетчик живых клеток
        
        if random_init:
            self._random_initialize()
        elif seed_pattern:
            self._apply_pattern(seed_pattern)
            
    def _random_initialize(self, probability=0.3):
        """Инициализирует сетку случайными состояниями.
        
        Args:
            probability (float): Вероятность того, что клетка будет жива (0-1).
        """
        self.living_cells_count = 0  # Сбрасываем счетчик
        for row in range(self.height):
            for col in range(self.width):
                if random.random() < probability:
                    self.grid[row][col].is_alive = True
                    self.living_cells_count += 1
                    
    def _apply_pattern(self, pattern):
        """Применяет предопределенный паттерн к сетке.
        
        Args:
            pattern (list): 2D-список, представляющий паттерн (True/False или 1/0).
        """
        self.living_cells_count = 0  # Сбрасываем счетчик
        pattern_height = len(pattern)
        pattern_width = len(pattern[0]) if pattern_height > 0 else 0
        
        # Центрирование паттерна в сетке
        start_row = (self.height - pattern_height) // 2
        start_col = (self.width - pattern_width) // 2
        
        for row in range(pattern_height):
            for col in range(pattern_width):
                if start_row + row < self.height and start_col + col < self.width:
                    is_alive = bool(pattern[row][col])
                    self.grid[start_row + row][start_col + col].is_alive = is_alive
                    if is_alive:
                        self.living_cells_count += 1
    
    def get_state_hash(self):
        """Возвращает хеш текущего состояния сетки для сравнения с предыдущими состояниями."""
        # Преобразуем сетку в строку из 1 и 0, затем вернем её хеш
        state = ''.join('1' if self.grid[row][col].is_alive else '0' 
                        for row in range(self.height) 
                        for col in range(self.width))
        return hash(state)
                        
    def get_neighbors(self, row, col):
        """Подсчитывает количество живых соседей для клетки с учетом перехода через края.
        
        Args:
            row (int): Строка клетки.
            col (int): Столбец клетки.
            
        Returns:
            int: Количество живых соседей.
        """
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue  # Пропускаем саму клетку
                
                # Вычисляем координаты соседа с учетом циклического перехода через края
                neighbor_row = (row + i) % self.height
                neighbor_col = (col + j) % self.width
                
                if self.grid[neighbor_row][neighbor_col].is_alive:
                    count += 1
        return count
    
    def update(self):
        """Обновляет все клетки в сетке до их следующих состояний."""
        # Сначала вычисляем следующие состояния для всех клеток
        for row in range(self.height):
            for col in range(self.width):
                live_neighbors = self.get_neighbors(row, col)
                self.grid[row][col].calculate_next_state(live_neighbors)
        
        # Сбрасываем счетчик живых клеток перед обновлением
        self.living_cells_count = 0
        
        # Затем обновляем все клетки
        for row in range(self.height):
            for col in range(self.width):
                self.grid[row][col].update()
                if self.grid[row][col].is_alive:
                    self.living_cells_count += 1
                    
    def __str__(self):
        """Возвращает строковое представление сетки."""
        return '\n'.join(' '.join(str(cell) for cell in row) for row in self.grid)


class GameOfLife:
    """Реализация «Игры жизни» Конвея."""
    
    # Предопределенные паттерны
    PATTERNS = {
        'glider': [
            [0, 1, 0],
            [0, 0, 1],
            [1, 1, 1]
        ],
        'blinker': [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ],
        'beacon': [
            [1, 1, 0, 0],
            [1, 1, 0, 0],
            [0, 0, 1, 1],
            [0, 0, 1, 1]
        ],
        'pulsar': [
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0]
        ]
    }
    
    def __init__(self, width=50, height=30, pattern=None, random_init=False):
        """Инициализирует симуляцию «Игры жизни».
        
        Args:
            width (int): Ширина сетки.
            height (int): Высота сетки.
            pattern (str): Имя предопределенного паттерна для инициализации.
            random_init (bool): Инициализировать ли случайными состояниями клеток.
        """
        seed_pattern = None
        if pattern and pattern in self.PATTERNS:
            seed_pattern = self.PATTERNS[pattern]
            
        self.grid = Grid(width, height, random_init, seed_pattern)
        self.generation = 0
        self.previous_states = []  # Список хешей предыдущих состояний
        self.stable_generations = 0  # Счетчик поколений со стабильным паттерном
        
    def next_generation(self):
        """Переходит к следующему поколению, обновляя все клетки сетки."""
        # Проверка на повторяющиеся состояния
        current_state = self.grid.get_state_hash()
        
        # Если текущее состояние совпадает с предыдущим, увеличиваем счетчик стабильных поколений
        if len(self.previous_states) > 0 and current_state == self.previous_states[-1]:
            self.stable_generations += 1
        else:
            self.stable_generations = 0
            
        # Ограничиваем список предыдущих состояний для экономии памяти
        self.previous_states.append(current_state)
        if len(self.previous_states) > 10:
            self.previous_states.pop(0)
            
        # Обновление сетки
        self.grid.update()
        self.generation += 1
        
        # Проверка на отсутствие живых клеток
        if self.grid.living_cells_count == 0:
            self.generation = 0  # Обнуляем счетчик поколений
            self.previous_states = []  # Сбрасываем историю состояний
            self.stable_generations = 0  # Сбрасываем счетчик стабильных поколений
            
        return {
            'is_stable': self.stable_generations >= 10,
            'living_cells': self.grid.living_cells_count
        }
    
    def run_simulation_console(self, generations, delay):
        """Запускает консольную симуляцию игры.
        
        Args:
            generations (int): Количество поколений для симуляции.
            delay (float): Задержка между поколениями в секундах.
        """
        for gen in range(generations):
            # Очистка экрана (работает в Windows и Unix-подобных системах)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Вывод текущего поколения
            print(f"Поколение: {self.generation}")
            print(self.grid)
            
            # Если все клетки мертвы, заканчиваем симуляцию
            if self.grid.living_cells_count == 0:
                print("\nСимуляция завершена: все клетки мертвы, счетчик обнулен.")
                break
                
            # Переход к следующему поколению
            result = self.next_generation()
            
            # Если паттерн стабилен 10 поколений, останавливаем симуляцию
            if result['is_stable']:
                print("\nПаттерн не меняется 10 поколений. Симуляция остановлена.")
                break
                
            # Задержка для наглядности
            time.sleep(delay)


def main():
    """Основная функция для запуска симуляции Игры жизни."""
    parser = argparse.ArgumentParser(description="Симуляция «Игры жизни» Конвея")
    parser.add_argument('--width', type=int, default=50, help='Ширина сетки')
    parser.add_argument('--height', type=int, default=20, help='Высота сетки')
    parser.add_argument('--generations', type=int, default=100, help='Количество поколений для симуляции')
    parser.add_argument('--delay', type=float, default=0.1, help='Задержка между поколениями в секундах')
    parser.add_argument('--pattern', choices=list(GameOfLife.PATTERNS.keys()), help='Начальный паттерн')
    parser.add_argument('--random', action='store_true', help='Инициализировать случайными состояниями клеток')
    args = parser.parse_args()
    
    pattern_data = None
    if args.pattern:
        pattern_data = GameOfLife.PATTERNS[args.pattern]
    
    game = GameOfLife(
        width=args.width,
        height=args.height,
        pattern=args.pattern,
        random_init=args.random
    )
    
    try:
        game.run_simulation_console(generations=args.generations, delay=args.delay)
    except KeyboardInterrupt:
        print("\nСимуляция остановлена пользователем")


if __name__ == "__main__":
    main()

