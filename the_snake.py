from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Константа координат центра игрового поля:
CENTER_OF_SCREEN = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Цвет ложной еды
FAKE_FOOD_COLOR = (105, 0, 198)

# Цвет камня
STONE_COLOR = (211, 211, 211)

# Количество камней на поле
AMOUNT_OF_STONES = 3

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Класс игровых объектов"""

    def __init__(self, position=CENTER_OF_SCREEN,
                 body_color=None) -> None:
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод отрисовки игрового объекта на экране"""
        raise NotImplementedError('Метод реализован в дочерних классах!')

    def draw_cell(self, position=None, color=None):
        """Метод отрисовки ячейки на экране"""
        color = color if color is not None else self.body_color
        position = position if position is not None else self.position
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока"""

    def __init__(self, occupied_cells, position=None,
                 body_color=APPLE_COLOR) -> None:
        super().__init__(position, body_color)
        self.randomize_position(occupied_cells)

    def randomize_position(self, occupied_cells):
        """Метод выбора случайной позиции"""
        while True:
            x = randint(0, GRID_WIDTH - 1)
            y = randint(0, GRID_HEIGHT - 1)
            if (x, y) not in occupied_cells:
                break
        self.position = (x * GRID_SIZE, y * GRID_SIZE)


class Snake(GameObject):
    """Класс змейки"""

    def __init__(self, position=CENTER_OF_SCREEN,
                 body_color=SNAKE_COLOR) -> None:
        super().__init__(position, body_color)
        self.reset()
        self.last = None

    def update_direction(self, direction):
        """Метод обновления направления после нажатия на кнопку"""
        self.direction = direction

    def move(self):
        """Метод движения змейки"""
        [head_position_x, head_position_y] = self.get_head_position()
        [direction_x, direction_y] = self.direction
        next_position = ((head_position_x + direction_x * GRID_SIZE)
                         % SCREEN_WIDTH,
                         (head_position_y + direction_y * GRID_SIZE)
                         % SCREEN_HEIGHT)
        self.positions.insert(0, next_position)
        self.last = self.positions.pop(-1)

    def draw(self):
        """Метод отрисовки змейки"""
        # Отрисовка головы змейки
        self.draw_cell(self.positions[0], self.body_color)
        # Затирание последнего сегмента
        if self.last:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Метод, возвращающий координаты головы змейки"""
        return self.positions[0]

    def reset(self):
        """Метод сброса змейки"""
        self.positions = [self.position]
        self.direction = RIGHT

    def decrease_length(self):
        """Метод уменьшения длины змейки"""
        position = self.positions.pop(-1)
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

    def add_last(self):
        """Метод добавления последнего сегмента"""
        self.positions.append(self.last)
        self.last = None


class FakeFood(Apple):
    """Класс ложной еды"""

    def __init__(self, occupied_cells, position=None,
                 body_color=FAKE_FOOD_COLOR) -> None:
        super().__init__(occupied_cells, position, body_color)


class Stone(Apple):
    """Класс камня"""

    def __init__(self, occupied_cells, position=None,
                 body_color=STONE_COLOR) -> None:
        super().__init__(occupied_cells, position, body_color)


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    Directions = {
        (LEFT, pg.K_UP): UP,
        (RIGHT, pg.K_UP): UP,
        (UP, pg.K_LEFT): LEFT,
        (DOWN, pg.K_LEFT): LEFT,
        (UP, pg.K_RIGHT): RIGHT,
        (DOWN, pg.K_RIGHT): RIGHT,
        (LEFT, pg.K_DOWN): DOWN,
        (RIGHT, pg.K_DOWN): DOWN
    }
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            direction = Directions.get((game_object.direction, event.key),
                                       game_object.direction)
            game_object.update_direction(direction)
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit


def main():
    """Основная функция"""
    # Инициализация PyGame:
    pg.init()
    occupied_cells = list(CENTER_OF_SCREEN)  # Список занятых ячеек
    apple = Apple(occupied_cells)
    occupied_cells.append(apple.position)
    snake = Snake()
    fake_food = FakeFood(occupied_cells)
    occupied_cells.append(fake_food.position)
    stones = list()
    for _ in range(AMOUNT_OF_STONES):
        stones.append(Stone(occupied_cells))
        occupied_cells.append(stones[-1].position)
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.move()
        head = snake.get_head_position()
        # Проверка на совпадение координат головы с яблоком
        if head == apple.position:
            snake.add_last()
            apple.randomize_position(occupied_cells)
            occupied_cells[1] = apple.position

        # Проверка на совпадение координат головы с ложной едой
        elif head == fake_food.position:
            if len(snake.positions) == 1:
                screen.fill(BOARD_BACKGROUND_COLOR)
                snake.reset()
                fake_food.randomize_position(occupied_cells)
                occupied_cells[2] = fake_food.position
            else:
                snake.decrease_length()
                fake_food = FakeFood(occupied_cells)
                occupied_cells[2] = fake_food.position

        # Проверка на столкновение змеи самой с собой
        if head in snake.positions[1:]:
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()

        # Проверка на столкновение змеи с камнем
        if any(stone.position == head for stone in stones):
            screen.fill(BOARD_BACKGROUND_COLOR)
            snake.reset()

        apple.draw_cell()
        fake_food.draw_cell()
        snake.draw()
        for i in range(AMOUNT_OF_STONES):
            stones[i].draw_cell()
        pg.display.update()


if __name__ == '__main__':
    main()
