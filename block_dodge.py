import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 600, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Dodge")

FPS = 60
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

CELL = 40
PLAYER_SIZE = CELL
PLAYER_STEP = CELL
ARENA = pygame.Rect(0, 0, WIDTH, HEIGHT)

FONT = pygame.font.Font(None, 28)
BIG_FONT = pygame.font.Font(None, 60)
CLOCK = pygame.time.Clock()


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


def draw_text(text, font, color, position):
    SCREEN.blit(font.render(text, True, color), position)


def reset_game():
    player = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    player.center = (WIDTH // 2, HEIGHT // 2)
    return player, [], 0.0, 0.0, False


def draw_game(player, hazards, score, elapsed, game_over):
    SCREEN.fill(BLACK)
    draw_text(f"Score: {score}", FONT, GREEN, (10, 10))
    draw_text(f"Time: {elapsed:.1f}s", FONT, GREEN, (10, 40))

    pygame.draw.rect(SCREEN, WHITE, ARENA, 1)

    for hazard in hazards:
        hazard.draw(SCREEN)

    pygame.draw.rect(SCREEN, WHITE, player)

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
    move_cooldown = 0.0
    move_delay = 0.11

    while running:
        dt = min(CLOCK.tick(FPS) / 1000.0, 0.04)
        move_cooldown = max(0.0, move_cooldown - dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_over and event.key == pygame.K_r:
                    player, hazards, elapsed, spawn_timer, game_over = reset_game()
                    move_cooldown = 0.0

        if not game_over:
            elapsed += dt
            score = int(elapsed * 10)
            keys = pygame.key.get_pressed()

            if move_cooldown <= 0:
                dx = dy = 0
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx = -PLAYER_STEP
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx = PLAYER_STEP
                elif keys[pygame.K_UP] or keys[pygame.K_w]:
                    dy = -PLAYER_STEP
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy = PLAYER_STEP

                if dx or dy:
                    candidate = player.move(dx, dy)
                    if ARENA.contains(candidate):
                        player = candidate
                    move_cooldown = move_delay

            spawn_timer += dt
            spawn_interval = max(0.34, 1.05 - elapsed * 0.009)
            if spawn_timer >= spawn_interval:
                hazards.append(Hazard(elapsed))
                spawn_timer = 0.0

            for hazard in hazards:
                hazard.update(dt)
                if hazard.rect.colliderect(player):
                    game_over = True

            hazards = [hazard for hazard in hazards if hazard.alive]
        else:
            score = int(elapsed * 10)

        draw_game(player, hazards, score, elapsed, game_over)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
