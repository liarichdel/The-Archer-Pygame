import pygame
import random
import sys
import math

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Archer")
icon = pygame.image.load('bow.png')
bg = pygame.image.load('10-01.jpg')
pygame.display.set_icon(icon)
clock = pygame.time.Clock()

playerImg = pygame.image.load('shooting-arrow.png')

white = (255, 255, 255)
black = (0, 0, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)
gray = (50, 50, 50)

class Entity:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Archer(Entity):
    def __init__(self):
        super().__init__(WIDTH//2, HEIGHT-300, 64, 64, blue)
        self.speed = 7

    def draw(self, surface):
        screen.blit(playerImg, (self.x, self.y))

    def move(self, key):
        if key[pygame.K_LEFT] and self.x > - 300:
            self.x -= self.speed
        if key[pygame.K_RIGHT] and self.x < WIDTH - 400:
            self.x += self.speed

class Bullet(Entity):
    def __init__(self, x, y ):
        super().__init__(x, y, 4, 15, yellow)
        self.speed = 12
        self.is_stuck = False
        self.offset_x = 0
        self.stuck_to = None

    def update(self):
        if not self.is_stuck:
            self.y -= self.speed
        elif self.stuck_to:
            self.x = self.stuck_to.x + self.offset_x

class Target:
    def __init__(self):
        self.base_radius = 40
        self.colors= [white, black, blue, red, yellow]
        self.x = random.randint(self.base_radius, WIDTH - self.base_radius)
        self.y = random.randint(50, 200)
        self.speed_x = random.choice([-4, -3, 3, 4])

    def update(self):
        self.x += self.speed_x
        if self.x - self.base_radius <= 0 or self.x + self.base_radius >= WIDTH:
            self.speed_x *= -1

    def draw(self, surface):
        for i in range(5):
            r = int(self.base_radius * (1 - i * 0.2))
            pygame.draw.circle(surface, self.colors[i], (int(self.x), int(self.y)), r)

    def get_rect(self):
        return pygame.Rect(self.x - 40, self.y - 40, 80, 80)

    def check_hit(self, bullet_x, bullet_y):
        distance = math.sqrt((bullet_x - self.x) ** 2 + (bullet_y - self.y) ** 2)
        if distance <= self.base_radius:
            if distance <= 8: return 100  # Kuning
            if distance <= 16: return 80  # Merah
            if distance <= 24: return 60  # Biru
            if distance <= 32: return 40  # Hitam
            return 20  # Putih
        return 0  # Tidak kena

archer = Archer()
targets = [Target() for _ in range(3)]
bullets = []
score = 0
time_limit = 60
start_ticks = pygame.time.get_ticks()
font = pygame.font.SysFont("Arial", 28, bold=True)
game_over = False

while True:
    screen.fill(gray)
    screen.blit(bg, (0,0))

    seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
    current_timer = time_limit - seconds_passed

    if current_timer <= 0:
        current_timer = 0
        game_over = True

    if not game_over:
        pass

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and not game_over:
            if event.key == pygame.K_SPACE:
                archer_center_x = archer.x + (playerImg.get_width() // 1.3)
                bullet_spawn_x = archer_center_x - 10
                bullets.append(Bullet(bullet_spawn_x, archer.y + 100))

    if not game_over:
        keys = pygame.key.get_pressed()
        archer.move(keys)

        for b in bullets[:]:
            if not b.is_stuck:
                b.update()

                bullet_mid_x = b.x + (b.width // 2)

                for t in targets[:]:
                    points = t.check_hit(bullet_mid_x, b.y)
                    if points > 0:
                        score += points
                        if points == 100: time_limit += 2

                        b.is_stuck = True
                        b.stuck_to = t
                        b.offset_x = b.x - t.x

                        targets.remove(t)
                        targets.append(Target())
                        break

                if not b.is_stuck and b.y < 0:
                    bullets.remove(b)

            else:
                bullets.remove(b)

        for t in targets:
            t.update()

    archer.draw(screen)
    for t in targets: t.draw(screen)
    for b in bullets: b.draw(screen)

    score_surf = font.render(f"SCORE: {score}", True, white)
    time_color = red if current_timer < 10 else white
    time_surf = font.render(f"TIME: {current_timer}s", True, time_color)

    screen.blit(score_surf, (20, 20))
    screen.blit(time_surf, (WIDTH - 150, 20))

    if game_over:
        final_surf = font.render(f"GAME OVER! TOTAL SCORE: {score}", True, yellow)
        screen.blit(final_surf, (WIDTH // 2 - 180, HEIGHT // 2))
        pygame.display.flip()
        pygame.time.wait(2000)

        pygame.quit()
        sys.exit()

    pygame.display.flip()
    clock.tick(60)

