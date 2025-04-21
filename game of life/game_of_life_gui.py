# game_of_life_gui.py
import pygame
import sys
import time
import argparse
from game_of_life import GameOfLife, Grid

class GameOfLifeGUI(GameOfLife):
    """Симуляция «Игры жизни» Конвея с графическим интерфейсом на Pygame."""
    
    CELL_SIZE = 15
    GRID_COLOR = (50, 50, 50)
    ALIVE_COLOR = (255, 255, 255)
    DEAD_COLOR = (0, 0, 0)
    BACKGROUND_COLOR = (10, 10, 10)
    
    def __init__(self, width=50, height=30, pattern=None, random_init=False):
        """Инициализирует симуляцию «Игры жизни» с графическим интерфейсом.
        
        Args:
            width (int): Ширина сетки.
            height (int): Высота сетки.
            pattern (str): Имя предопределенного паттерна для инициализации.
            random_init (bool): Инициализировать ли случайными состояниями клеток.
        """
        super().__init__(width, height, pattern, random_init)
        
        pygame.init()
        pygame.display.set_caption("Игра жизни Конвея")
        
        self.window_width = width * self.CELL_SIZE
        self.window_height = height * self.CELL_SIZE
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        self.clock = pygame.time.Clock()
        self.fps = 10  # Кадров в секунду (скорость симуляции)
        self.running = False  # Изначально симуляция на паузе
        self.message = None  # Сообщение для отображения
        self.message_time = 0  # Время отображения сообщения
        
    def draw_grid(self):
        """Отрисовывает сетку и клетки."""
        self.screen.fill(self.BACKGROUND_COLOR)
        
        # Отрисовка клеток
        for row in range(self.grid.height):
            for col in range(self.grid.width):
                color = self.ALIVE_COLOR if self.grid.grid[row][col].is_alive else self.DEAD_COLOR
                rect = pygame.Rect(
                    col * self.CELL_SIZE,
                    row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, self.GRID_COLOR, rect, 1)
        
        # Отображение номера поколения
        font = pygame.font.SysFont(None, 24)
        gen_text = font.render(f"Поколение: {self.generation}", True, self.ALIVE_COLOR)
        self.screen.blit(gen_text, (10, 10))
        
        # Отображение сообщения, если оно есть
        if self.message:
            font = pygame.font.SysFont(None, 30)
            message_surface = font.render(self.message['text'], True, self.message['color'])
            message_rect = message_surface.get_rect(center=(self.window_width//2, self.window_height//2))
            self.screen.blit(message_surface, message_rect)
            
            # Проверяем, нужно ли удалить сообщение
            if pygame.time.get_ticks() - self.message_time > 5000:  # Сообщение исчезает через 5 секунд
                self.message = None
        
    def handle_events(self):
        """Обработка событий pygame."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Переключение паузы/воспроизведения
                    self.running = not self.running
                    self.message = None  # Убираем сообщение при нажатии пробела
                elif event.key == pygame.K_r:
                    # Сброс со случайной инициализацией
                    self.grid = Grid(self.grid.width, self.grid.height, random_init=True)
                    self.generation = 0
                    self.previous_states = []
                    self.stable_generations = 0
                    self.message = None
                elif event.key == pygame.K_c:
                    # Очистка сетки
                    self.grid = Grid(self.grid.width, self.grid.height)
                    self.generation = 0
                    self.previous_states = []
                    self.stable_generations = 0
                    self.message = None
                elif event.key == pygame.K_UP:
                    # Увеличение скорости
                    self.fps = min(60, self.fps + 5)
                elif event.key == pygame.K_DOWN:
                    # Уменьшение скорости
                    self.fps = max(1, self.fps - 5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Переключение состояния клетки при клике мышью
                x, y = pygame.mouse.get_pos()
                col = x // self.CELL_SIZE
                row = y // self.CELL_SIZE
                
                if 0 <= row < self.grid.height and 0 <= col < self.grid.width:
                    current_state = self.grid.grid[row][col].is_alive
                    self.grid.grid[row][col].is_alive = not current_state
                    
                    # Обновляем счетчик живых клеток
                    if self.grid.grid[row][col].is_alive:
                        self.grid.living_cells_count += 1
                    else:
                        self.grid.living_cells_count -= 1
    
    def show_message(self, text, color=(255, 0, 0)):
        """Отображает сообщение на экране.
        
        Args:
            text (str): Текст сообщения.
            color (tuple): Цвет текста в формате RGB.
        """
        self.message = {'text': text, 'color': color}
        self.message_time = pygame.time.get_ticks()
    
    def run_simulation(self):
        """Запуск симуляции с графическим интерфейсом."""
        while True:
            self.handle_events()
            
            if self.running:
                # Проверяем наличие живых клеток используя счетчик
                if self.grid.living_cells_count == 0:
                    self.running = False
                    self.generation = 0  # Обнуляем счетчик поколений
                    self.show_message("Все клетки мертвы. Счетчик поколений обнулен.", (255, 0, 0))
                else:
                    # Продолжаем симуляцию, если есть живые клетки
                    result = self.next_generation()
                    
                    # Если паттерн стабилен 10 поколений, останавливаем симуляцию
                    if result['is_stable']:
                        self.running = False
                        self.show_message("Паттерн не меняется 10 поколений. Симуляция остановлена.", (255, 255, 0))
            
            self.draw_grid()
            pygame.display.flip()
            self.clock.tick(self.fps)


def main():
    """Основная функция для запуска симуляции «Игры жизни» с графическим интерфейсом."""
    parser = argparse.ArgumentParser(description="Симуляция «Игры жизни» Конвея с графическим интерфейсом")
    parser.add_argument('--width', type=int, default=50, help='Ширина сетки')
    parser.add_argument('--height', type=int, default=30, help='Высота сетки')
    parser.add_argument('--pattern', choices=list(GameOfLife.PATTERNS.keys()), help='Начальный шаблон')
    parser.add_argument('--random', action='store_true', help='Инициализировать случайным образом')
    args = parser.parse_args()
    
    game = GameOfLifeGUI(
        width=args.width,
        height=args.height,
        pattern=args.pattern,
        random_init=args.random
    )
    game.run_simulation()


if __name__ == "__main__":
    main()

