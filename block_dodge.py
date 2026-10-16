import pygame
import random
import sys

# -------------------- Configuration --------------------
pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Block Dodge")

FPS = 60
BG = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (255, 255, 255)
BOUNDARY_COLOR = (255, 255, 255)
HAZARD_COLOR = (255, 0, 0)
MUTED = (255, 255, 255)
ACCENT = (255, 255, 255)

CELL = 30
PLAYER_SIZE = CELL
PLAYER_STEP = CELL

# The arena is a rectangle one cell wider and taller than the player.
ARENA_W = 21 * CELL
ARENA_H = 15 * CELL
ARENA = pygame.Rect((WIDTH - ARENA_W) // 2, (HEIGHT - ARENA_H) // 2 + 15,
                    ARENA_W, ARENA_H)

FONT = pygame.font.Font(None, 28)
BIG_FONT = pygame.font.Font(None, 60)
SMALL_FONT = pygame.font.Font(None, 22)
CLOCK = pygame.time.Clock()

class Hazard:
    def __init__(self, elapsed):
        self.horizontal = random.choice([True, False])
        self.speed = random.uniform(210, 300) + min(elapsed * 2.2, 170)
        self.rect = self.make_rect()
        self.alive = True

    def make_rect(self):
        # Hazards are long bars, moving along only one axis.
        if self.horizontal:
            length = random.randint(3, 6) * CELL
            y = random.randrange(ARENA.top, ARENA.bottom - CELL + 1, CELL)
            if random.choice([True, False]):
                x = ARENA.left - length
                self.direction = 1
            else:
                x = ARENA.right
                self.direction = -1
            return pygame.Rect(x, y, length, CELL)
        else:
            length = random.randint(3, 5) * CELL
            x = random.randrange(ARENA.left, ARENA.right - CELL + 1, CELL)
            if random.choice([True, False]):
                y = ARENA.top - length
                self.direction = 1
            else:
                y = ARENA.bottom
                self.direction = -1
            return pygame.Rect(x, y, CELL, length)

    def update(self, dt):
        distance = self.speed * dt * self.direction
        if self.horizontal:
            self.rect.x += round(distance)
        else:
            self.rect.y += round(distance)

        if (self.horizontal and
            (self.rect.right < ARENA.left or self.rect.left > ARENA.right)):
            self.alive = False
        elif (not self.horizontal and
              (self.rect.bottom < ARENA.top or self.rect.top > ARENA.bottom)):
            self.alive = False

    def draw(self, surface):
        pygame.draw.rect(surface, HAZARD_COLOR, self.rect)


def draw_text(text, font, color, center):
    image = font.render(text, True, color)
    SCREEN.blit(image, image.get_rect(center=center))


def reset_game():
    player = pygame.Rect(0, 0, PLAYER_SIZE, PLAYER_SIZE)
    player.center = ARENA.center
    return player, [], 0.0, 0.0, False


def draw_game(player, hazards, score, elapsed, game_over):
    SCREEN.fill(BG)

    # Plain text and simple rectangles.
    score_text = FONT.render(f"Score: {score}", True, WHITE)
    SCREEN.blit(score_text, (WIDTH - score_text.get_width() - 20, 15))
    time_text = SMALL_FONT.render(f"Time: {elapsed:.1f}s", True, WHITE)
    SCREEN.blit(time_text, (WIDTH - time_text.get_width() - 20, 42))

    pygame.draw.rect(SCREEN, BOUNDARY_COLOR, ARENA, 2)

    for hazard in hazards:
        hazard.draw(SCREEN)

    pygame.draw.rect(SCREEN, PLAYER_COLOR, player)

    if game_over:
        draw_text("GAME OVER", BIG_FONT, WHITE, (WIDTH // 2, HEIGHT // 2 - 55))
        draw_text(f"Final score: {score} | Survived: {elapsed:.1f}s",
                  FONT, WHITE, (WIDTH // 2, HEIGHT // 2))
        draw_text("Press R to restart or ESC to quit",
                  FONT, WHITE, (WIDTH // 2, HEIGHT // 2 + 48))

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
                if game_over and event.key == pygame.K_r:
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
