from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Класс игровых объектов"""

    def __init__(self) -> None:
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = None

    def draw(self):
        """Метод отрисочки игрового объекта на экране"""
        pass


class Apple(GameObject):
    """Класс яблока"""

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def draw(self):
        """Метод отрисовки яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self):
        """Метод выбора случайной позиции"""
        x = randint(0, GRID_WIDTH - 1)
        y = randint(0, GRID_HEIGHT - 1)
        self.position = (x * GRID_SIZE, y * GRID_SIZE)


class Snake(GameObject):
    """Класс змейки"""

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Метод обновления направления после нажатия на кнопку"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод движения змейки"""
        self.update_direction()
        next_position = ((self.positions[0][0] + self.direction[0] * GRID_SIZE)
                         % SCREEN_WIDTH,
                         (self.positions[0][1] + self.direction[1] * GRID_SIZE)
                         % SCREEN_HEIGHT)
        self.positions.insert(0, next_position)
        self.last = self.positions[-1]
        del self.positions[-1]

    def draw(self):
        """Метод отрисовки змейки"""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)
        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Метод, возвращающий координаты головы змейки"""
        return self.positions[0]

    def reset(self):
        """Метод сброса змейки"""
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
        self.__init__()


class FakeFood(Apple):
    """Класс ложной еды"""

    def __init__(self):
        super().__init__()
        self.body_color = FAKE_FOOD_COLOR


class Stone(Apple):
    """Класс камня"""

    def __init__(self):
        super().__init__()
        self.body_color = STONE_COLOR


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основная функция"""
    # Инициализация PyGame:
    pygame.init()
    apple = Apple()
    snake = Snake()
    fake_food = FakeFood()
    stones = list()
    for _ in range(AMOUNT_OF_STONES):
        stones.append(Stone())
    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        apple.draw()
        fake_food.draw()
        snake.move()
        snake.draw()
        head = snake.get_head_position()
        for i in range(AMOUNT_OF_STONES):
            stones[i].draw()
        pygame.display.update()
        # Проверка на совпадение координат головы с яблоком
        if head == apple.position:
            snake.positions.append(snake.last)
            snake.length += 1
            apple = Apple()

        # Проверка на совпадение координат головы с ложной едой
        if head == fake_food.position:
            if snake.length == 1:
                snake.reset()
                fake_food = FakeFood()
            else:
                position = snake.positions.pop(-1)
                snake.length -= 1
                rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)
                fake_food = FakeFood()

        # Проверка на столкновение змеи самой с собой
        if head in snake.positions[1:-1]:
            snake.reset()

        # Проверка на столкновение змеи с камнем
        if any(stone.position == head for stone in stones):
            snake.reset()


if __name__ == '__main__':
    main()
