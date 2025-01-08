import pygame
import random
from collections import deque

class Cube:
    rows = 20
    w = 500

    def __init__(self, start, dirx=1, diry=0, color=(255, 0, 0)):
        self.pos = start
        self.dirx = dirx
        self.diry = diry
        self.color = color

    def move(self, dirx, diry):
        self.dirx = dirx
        self.diry = diry
        self.pos = (self.pos[0] + self.dirx, self.pos[1] + self.diry)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i, j = self.pos
        pygame.draw.rect(surface, self.color, (i * dis + 1, j * dis + 1, dis - 2, dis - 2))
        if eyes:
            centre = dis // 2
            radius = 3
            circleMiddle = (i * dis + centre - radius, j * dis + 8)
            circleMiddle2 = (i * dis + dis - radius * 2, j * dis + 8)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle, radius)
            pygame.draw.circle(surface, (0, 0, 0), circleMiddle2, radius)


class Snake:
    def __init__(self, color, pos):
        self.body = []
        self.turns = {}
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.dirx = 0
        self.diry = 1
        self.path = []

    def get_neighbors(self, pos):
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_x = pos[0] + dx
            new_y = pos[1] + dy
            if (0 <= new_x < Cube.rows and
                    0 <= new_y < Cube.rows and
                    (new_x, new_y) not in [cube.pos for cube in self.body[:-1]]):
                neighbors.append((new_x, new_y))
        return neighbors

    def bfs(self, start, goal):
        queue = deque([[start]])
        visited = {start}

        while queue:
            path = queue.popleft()
            current = path[-1]

            if current == goal:
                return path

            for neighbor in self.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)
        return None

    def move_ai(self, snack_pos):
        if not self.path:
            self.path = self.bfs(self.head.pos, snack_pos)
            if not self.path:
                # If no path to food, try to follow tail
                self.path = self.bfs(self.head.pos, self.body[-1].pos)
                if not self.path:
                    return False

        if len(self.path) > 1:
            next_pos = self.path[1]
            self.dirx = next_pos[0] - self.head.pos[0]
            self.diry = next_pos[1] - self.head.pos[1]
            self.path = self.path[1:]
            self.turns[self.head.pos[:]] = [self.dirx, self.diry]

        return self.update_position()

    def move_manual(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.dirx != 1:
                    self.dirx = -1
                    self.diry = 0
                    self.turns[self.head.pos[:]] = [self.dirx, self.diry]
                elif event.key == pygame.K_RIGHT and self.dirx != -1:
                    self.dirx = 1
                    self.diry = 0
                    self.turns[self.head.pos[:]] = [self.dirx, self.diry]
                elif event.key == pygame.K_UP and self.diry != 1:
                    self.dirx = 0
                    self.diry = -1
                    self.turns[self.head.pos[:]] = [self.dirx, self.diry]
                elif event.key == pygame.K_DOWN and self.diry != -1:
                    self.dirx = 0
                    self.diry = 1
                    self.turns[self.head.pos[:]] = [self.dirx, self.diry]

        return self.update_position()

    def update_position(self):
        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0], turn[1])
                if i == len(self.body) - 1:
                    self.turns.pop(p)
            else:
                if c.dirx == -1 and c.pos[0] <= 0:
                    c.pos = (c.rows - 1, c.pos[1])
                elif c.dirx == 1 and c.pos[0] >= c.rows - 1:
                    c.pos = (0, c.pos[1])
                elif c.diry == 1 and c.pos[1] >= c.rows - 1:
                    c.pos = (c.pos[0], 0)
                elif c.diry == -1 and c.pos[1] <= 0:
                    c.pos = (c.pos[0], c.rows - 1)
                else:
                    c.move(c.dirx, c.diry)
        return True

    def reset(self, pos):
        self.head = Cube(pos)
        self.body = [self.head]
        self.turns = {}
        self.dirx = 0
        self.diry = 1
        self.path = []

    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirx, tail.diry

        if dx == 1 and dy == 0:
            self.body.append(Cube((tail.pos[0] - 1, tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(Cube((tail.pos[0] + 1, tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] - 1)))
        elif dx == 0 and dy == -1:
            self.body.append(Cube((tail.pos[0], tail.pos[1] + 1)))

        self.body[-1].dirx = dx
        self.body[-1].diry = dy

    def draw(self, surface):
        for i, c in enumerate(self.body):
            c.draw(surface, i == 0)


class Game:
    def __init__(self):
        pygame.init()
        self.width = 500
        self.rows = 20
        self.window = pygame.display.set_mode((self.width, self.width))
        pygame.display.set_caption('Snake Game')
        self.font = pygame.font.SysFont(None, 36)
        self.running = True

    def draw_grid(self):
        size_btwn = self.width // self.rows
        x = y = 0
        for _ in range(self.rows):
            x += size_btwn
            y += size_btwn
            pygame.draw.line(self.window, (40, 40, 40), (x, 0), (x, self.width))
            pygame.draw.line(self.window, (40, 40, 40), (0, y), (self.width, y))

    def draw_menu(self, options, selected=0):
        self.window.fill((0, 0, 0))
        y_pos = self.width // 3

        title = self.font.render("Snake Game", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, y_pos - 50))
        self.window.blit(title, title_rect)

        for i, option in enumerate(options):
            color = (0, 255, 0) if i == selected else (255, 255, 255)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.width // 2, y_pos + i * 50))
            self.window.blit(text, rect)

        pygame.display.update()

    def random_snack(self, snake):
        while True:
            x = random.randrange(self.rows)
            y = random.randrange(self.rows)
            if len(list(filter(lambda z: z.pos == (x, y), snake.body))) > 0:
                continue
            else:
                break
        return (x, y)

    def menu(self):
        options = ["Play Manual", "Play AI", "Exit"]
        selected = 0
        while self.running:
            self.draw_menu(options, selected)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == "Exit":
                            return "exit"
                        return options[selected]

            pygame.time.delay(100)
        return "exit"

    def game_over_screen(self, score):
        options = ["Play Again", "Exit"]
        selected = 0
        while self.running:
            self.window.fill((0, 0, 0))

            game_over = self.font.render("Game Over!", True, (255, 0, 0))
            score_text = self.font.render(f"Score: {score}", True, (255, 255, 255))
            game_over_rect = game_over.get_rect(center=(self.width // 2, self.width // 3 - 50))
            score_rect = score_text.get_rect(center=(self.width // 2, self.width // 3))
            self.window.blit(game_over, game_over_rect)
            self.window.blit(score_text, score_rect)

            y_pos = self.width // 2
            for i, option in enumerate(options):
                color = (0, 255, 0) if i == selected else (255, 255, 255)
                text = self.font.render(option, True, color)
                rect = text.get_rect(center=(self.width // 2, y_pos + i * 50))
                self.window.blit(text, rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "exit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        if options[selected] == "Exit":
                            return "exit"
                        return "play_again"

            pygame.time.delay(100)
        return "exit"

    def play_game(self, mode):
        snake = Snake((255, 0, 0), (10, 10))
        snack = Cube(self.random_snack(snake), color=(0, 255, 0))
        clock = pygame.time.Clock()

        while self.running:
            pygame.time.delay(50)
            clock.tick(10)

            if mode == "Play AI":
                if not snake.move_ai(snack.pos):
                    return len(snake.body)
            else:
                if not snake.move_manual():
                    return len(snake.body)

            if snake.body[0].pos == snack.pos:
                snake.addCube()
                snack = Cube(self.random_snack(snake), color=(0, 255, 0))
                snake.path = []

            for x in range(len(snake.body)):
                if snake.body[x].pos in list(map(lambda z: z.pos, snake.body[x + 1:])):
                    return len(snake.body)

            self.window.fill((0, 0, 0))
            self.draw_grid()
            snake.draw(self.window)
            snack.draw(self.window)
            pygame.display.update()

        return len(snake.body)

    def run(self):
        while self.running:
            choice = self.menu()
            if choice == "exit":
                break

            score = self.play_game(choice)

            if not self.running:
                break

            over_choice = self.game_over_screen(score)
            if over_choice == "exit":
                break

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()