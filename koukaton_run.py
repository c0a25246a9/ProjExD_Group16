import pygame
import random

pygame.init()

WIDTH = 800
HEIGHT = 600
GROUND_Y = 500

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Temple Run Side Scroll")
clock = pygame.time.Clock()

# 色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (50, 100, 255)
YELLOW = (255, 220, 0)
SKY = (120, 200, 255)
BROWN = (120, 80, 40)

# フォント
font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 35)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(120, 420, 60, 80)
        self.y_speed = 0
        self.jump = False

    def update(self):
        if self.jump:
            self.rect.y += self.y_speed
            self.y_speed += 1

            if self.rect.y >= 420:
                self.rect.y = 420
                self.jump = False

    def jump_action(self):
        if not self.jump:
            self.jump = True
            self.y_speed = -18

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


class Obstacle:
    def __init__(self, speed):
        height = random.randint(40, 80)
        self.rect = pygame.Rect(WIDTH, GROUND_Y - height, 50, height)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


class Coin:
    def __init__(self, speed):
        y = random.randint(300, 430)
        self.rect = pygame.Rect(WIDTH, y, 30, 30)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed

    def draw(self):
        pygame.draw.circle(screen, YELLOW, self.rect.center, 15)


class Game:
    def __init__(self):
        self.player = Player()
        self.obstacles = []
        self.coins = []

        self.score = 0
        self.coin_count = 0

        self.obstacle_timer = 0
        self.coin_timer = 0

        self.speed = 8
        self.game_over = False

    def reset(self):
        self.__init__()

    def create_obstacle(self):
        self.obstacles.append(Obstacle(self.speed))

    def create_coin(self):
        self.coins.append(Coin(self.speed))

    def update(self):
        if self.game_over:
            return

        self.player.update()

        self.obstacle_timer += 1
        self.coin_timer += 1

        if self.obstacle_timer > 50:
            self.create_obstacle()
            self.obstacle_timer = 0

        if self.coin_timer > 80:
            self.create_coin()
            self.coin_timer = 0

        # 障害物更新
        for obstacle in self.obstacles[:]:
            obstacle.speed = self.speed
            obstacle.update()

            if obstacle.rect.colliderect(self.player.rect):
                self.game_over = True

            if obstacle.rect.x < -100:
                self.obstacles.remove(obstacle)
                self.score += 1

        # コイン更新
        for coin in self.coins[:]:
            coin.speed = self.speed
            coin.update()

            if coin.rect.colliderect(self.player.rect):
                self.coin_count += 1
                self.coins.remove(coin)

            elif coin.rect.x < -50:
                self.coins.remove(coin)

        self.speed = 8 + self.score // 10

    def draw(self):
        # 背景
        screen.fill(SKY)

        # 地面
        pygame.draw.rect(screen, GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, 10))

        # 雲
        for i in range(5):
            cloud_x = (pygame.time.get_ticks() // 15 + i * 200) % 1000
            pygame.draw.circle(screen, WHITE, (WIDTH - cloud_x, 100), 30)
            pygame.draw.circle(screen, WHITE, (WIDTH - cloud_x + 30, 100), 25)

        # プレイヤー
        self.player.draw()

        # 障害物
        for obstacle in self.obstacles:
            obstacle.draw()

        # コイン
        for coin in self.coins:
            coin.draw()

        # スコア表示
        score_text = small_font.render(f"Score : {self.score}", True, BLACK)
        coin_text = small_font.render(f"Coins : {self.coin_count}", True, BLACK)

        screen.blit(score_text, (20, 20))
        screen.blit(coin_text, (20, 60))

        # ゲームオーバー
        if self.game_over:
            over_text = font.render("GAME OVER", True, RED)
            retry_text = small_font.render("Press R to Retry", True, BLACK)

            screen.blit(over_text, (220, 250))
            screen.blit(retry_text, (260, 330))


# ゲーム作成
game = Game()

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game.game_over:
                    game.player.jump_action()

            if event.key == pygame.K_r:
                if game.game_over:
                    game.reset()

    game.update()
    game.draw()

    pygame.display.update()

pygame.quit()