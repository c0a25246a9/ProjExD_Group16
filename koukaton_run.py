import pygame
import random

pygame.init()

# 画面サイズ
WIDTH = 800
HEIGHT = 600
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

# 地面
GROUND_Y = 500

# プレイヤー
player = pygame.Rect(120, 420, 60, 80)
player_y_speed = 0
jump = False

# 障害物
obstacles = []
obstacle_timer = 0
obstacle_speed = 8

# コイン
coins = []
coin_timer = 0
coin_count = 0

# スコア
score = 0

# ゲーム状態
game_over = False


# 障害物作成

def create_obstacle():
    height = random.randint(40, 80)
    obstacle = pygame.Rect(WIDTH, GROUND_Y - height, 50, height)
    obstacles.append(obstacle)


# コイン作成

def create_coin():
    y = random.randint(300, 430)
    coin = pygame.Rect(WIDTH, y, 30, 30)
    coins.append(coin)


running = True
while running:
    clock.tick(60)

    # 背景
    screen.fill(SKY)

    # 地面
    pygame.draw.rect(screen, GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))

    # 地面ライン
    pygame.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, 10))

    # 雲
    for i in range(5):
        cloud_x = (pygame.time.get_ticks() // 15 + i * 200) % 1000
        pygame.draw.circle(screen, WHITE, (WIDTH - cloud_x, 100), 30)
        pygame.draw.circle(screen, WHITE, (WIDTH - cloud_x + 30, 100), 25)

    # イベント
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if not game_over:
                if event.key == pygame.K_SPACE:
                    if not jump:
                        jump = True
                        player_y_speed = -18

            if game_over:
                if event.key == pygame.K_r:
                    obstacles.clear()
                    coins.clear()
                    score = 0
                    coin_count = 0
                    obstacle_speed = 8
                    player.y = 420
                    game_over = False

    # ジャンプ
    if jump:
        player.y += player_y_speed
        player_y_speed += 1

        if player.y >= 420:
            player.y = 420
            jump = False

    # プレイヤー描画
    pygame.draw.rect(screen, BLUE, player)

    # 障害物生成
    obstacle_timer += 1
    if obstacle_timer > 50:
        create_obstacle()
        obstacle_timer = 0

    # コイン生成
    coin_timer += 1
    if coin_timer > 80:
        create_coin()
        coin_timer = 0

    # 障害物移動
    for obstacle in obstacles[:]:
        obstacle.x -= obstacle_speed

        pygame.draw.rect(screen, RED, obstacle)

        if obstacle.colliderect(player):
            game_over = True

        if obstacle.x < -100:
            obstacles.remove(obstacle)
            score += 1

    # コイン移動
    for coin in coins[:]:
        coin.x -= obstacle_speed

        pygame.draw.circle(screen, YELLOW, coin.center, 15)

        if coin.colliderect(player):
            coin_count += 1
            coins.remove(coin)

        elif coin.x < -50:
            coins.remove(coin)

    # スピードアップ
    obstacle_speed = 8 + score // 10

    # スコア表示
    score_text = small_font.render(f"Score : {score}", True, BLACK)
    coin_text = small_font.render(f"Coins : {coin_count}", True, BLACK)

    screen.blit(score_text, (20, 20))
    screen.blit(coin_text, (20, 60))

    # ゲームオーバー
    if game_over:
        over_text = font.render("GAME OVER", True, RED)
        retry_text = small_font.render("Press R to Retry", True, BLACK)

        screen.blit(over_text, (220, 250))
        screen.blit(retry_text, (260, 330))

    pygame.display.update()

pygame.quit()