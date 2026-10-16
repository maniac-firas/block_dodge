import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Dodge - Space Physics")

FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

CELL = 40
ARENA = pygame.Rect(0, 0, WIDTH, HEIGHT)

FONT = pygame.font.Font(None, 28)
BIG_FONT = pygame.font.Font(None, 60)
CLOCK = pygame.time.Clock()


class Player:
    def __init__(self):
        self.pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.vel = pygame.math.Vector2(0, 0)
        self.angle = 0.0
        self.turn_speed = 120.0
        self.thrust_accel = 200.0
        self.drag = 1.0
        self.size = 18

    def get_vertices(self):
        nose = self.pos + pygame.math.Vector2(0, -self.size).rotate(self.angle)
        left = self.pos + pygame.math.Vector2(-self.size * 0.7, self.size * 0.7).rotate(self.angle)
        right = self.pos + pygame.math.Vector2(self.size * 0.7, self.size * 0.7).rotate(self.angle)
        return [nose, left, right]

    def update(self, dt, keys):
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.angle -= self.turn_speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.angle += self.turn_speed * dt

        forward = pygame.math.Vector2(0, -1).rotate(self.angle)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel += forward * self.thrust_accel * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel -= forward * (self.thrust_accel * 0.5) * dt

        self.vel -= self.vel * self.drag * dt
        self.pos += self.vel * dt

        margin = 15
        if self.pos.x < margin:
            self.pos.x = margin
            self.vel.x = 0
        elif self.pos.x > WIDTH - margin:
            self.pos.x = WIDTH - margin
            self.vel.x = 0

        if self.pos.y < margin:
            self.pos.y = margin
            self.vel.y = 0
        elif self.pos.y > HEIGHT - margin:
            self.pos.y = HEIGHT - margin
            self.vel.y = 0

    def draw(self, surface):
        pygame.draw.polygon(surface, WHITE, self.get_vertices())


class Hazard:
    def __init__(self, elapsed):
        self.horizontal = random.choice([True, False])
        self.speed = random.uniform(210, 300) + min(elapsed * 2.2, 170)
        self.rect = self.make_rect()
        self.alive = True

    def make_rect(self):
        if self.horizontal:
            length = random.randint(3, 6) * CELL
            y = random.randrange(0, HEIGHT - CELL + 1, CELL)
            if random.choice([True, False]):
                x = -length
                self.direction = 1
            else:
                x = WIDTH
                self.direction = -1
            return pygame.Rect(x, y, length, CELL)

        length = random.randint(3, 5) * CELL
        x = random.randrange(0, WIDTH - CELL + 1, CELL)
        if random.choice([True, False]):
            y = -length
            self.direction = 1
        else:
            y = HEIGHT
            self.direction = -1
        return pygame.Rect(x, y, CELL, length)

    def update(self, dt):
        distance = round(self.speed * dt * self.direction)
        if self.horizontal:
            self.rect.x += distance
            if self.rect.right < 0 or self.rect.left > WIDTH:
                self.alive = False
        else:
            self.rect.y += distance
            if self.rect.bottom < 0 or self.rect.top > HEIGHT:
                self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, RED, self.rect)


def check_polygon_rect_collision(poly_points, rect):
    rect_points = [
        pygame.math.Vector2(rect.left, rect.top),
        pygame.math.Vector2(rect.right, rect.top),
        pygame.math.Vector2(rect.right, rect.bottom),
        pygame.math.Vector2(rect.left, rect.bottom),
    ]

    for shape in (poly_points, rect_points):
        for i in range(len(shape)):
            p1 = shape[i]
            p2 = shape[(i + 1) % len(shape)]
            edge = p2 - p1
            normal = pygame.math.Vector2(-edge.y, edge.x)
            if normal.length() == 0:
                continue
            normal = normal.normalize()

            min_a = min(p.dot(normal) for p in poly_points)
            max_a = max(p.dot(normal) for p in poly_points)
            min_b = min(p.dot(normal) for p in rect_points)
            max_b = max(p.dot(normal) for p in rect_points)

            if max_a < min_b or max_b < min_a:
                return False
    return True


def draw_text(text, font, color, position):
    SCREEN.blit(font.render(text, True, color), position)


def reset_game():
    player = Player()
    return player, [], 0.0, 0.0, False


def draw_game(player, hazards, score, elapsed, game_over):
    SCREEN.fill(BLACK)
    draw_text(f"Score: {score}", FONT, GREEN, (10, 10))
    draw_text(f"Time: {elapsed:.1f}s", FONT, GREEN, (10, 40))

    pygame.draw.rect(SCREEN, WHITE, ARENA, 1)

    for hazard in hazards:
        hazard.draw(SCREEN)

    player.draw(SCREEN)

    if game_over:
        title = BIG_FONT.render("GAME OVER", True, WHITE)
        final_score = FONT.render(
            f"Final score: {score}   Time: {elapsed:.1f}s", True, GREEN
        )
        restart = FONT.render("Press R to restart or ESC to quit", True, WHITE)
        SCREEN.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50)))
        SCREEN.blit(final_score, final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        SCREEN.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

    pygame.display.flip()


def main():
    player, hazards, elapsed, spawn_timer, game_over = reset_game()
    running = True

    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.04)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_over and event.key == pygame.K_r:
                    player, hazards, elapsed, spawn_timer, game_over = reset_game()

        if not game_over:
            elapsed += dt
            score = int(elapsed * 10)
            keys = pygame.key.get_pressed()

            player.update(dt, keys)

            spawn_timer += dt
            spawn_interval = max(0.34, 1.05 - elapsed * 0.009)
            if spawn_timer >= spawn_interval:
                hazards.append(Hazard(elapsed))
                spawn_timer = 0.0

            player_vertices = player.get_vertices()
            for hazard in hazards:
                hazard.update(dt)
                if check_polygon_rect_collision(player_vertices, hazard.rect):
                    game_over = True

            hazards = [hazard for hazard in hazards if hazard.alive]
        else:
            score = int(elapsed * 10)

        draw_game(player, hazards, score, elapsed, game_over)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()