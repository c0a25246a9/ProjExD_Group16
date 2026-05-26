import math
import os
import random
import sys
import time
import pygame as pg

# 定数設定
WIDTH = 800
HEIGHT = 600
GROUND_Y = 500

# 色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (50, 100, 255)
YELLOW = (255, 220, 0)
SKY = (120, 200, 255)
BROWN = (120, 80, 40)

def check_bound_horizontal(obj_rct: pg.Rect) -> bool:
    """
    オブジェクトが画面の左端より外に出たかを判定する
    """
    if obj_rct.right < 0:
        return True
    return False

class Bird(pg.sprite.Sprite):
    """
    プレイヤー（青い四角）に関するクラス
    """
    def __init__(self, xy: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((60, 80))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = xy
        
        self.y_speed = 0
        self.on_ground = False
        self.jump_force = -18
        self.gravity = 1
        self.invincible = 0  # 無敵時間さん

    def update(self, key_lst: list[bool]):
        # 重力処理
        self.y_speed += self.gravity
        self.rect.y += self.y_speed

        # 地面判定
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.y_speed = 0
            self.on_ground = True
        else:
            self.on_ground = False

        if self.invincible > 0:
            self.invincible -= 1 # 無敵時間のカウントダウン

        # ジャンプ入力
        if key_lst[pg.K_SPACE] and self.on_ground:
            self.y_speed = self.jump_force
            self.on_ground = False

class Obstacle(pg.sprite.Sprite):
    """
    障害物（赤い矩形）に関するクラス
    """
    def __init__(self, speed):
        super().__init__()
        height = random.randint(40, 80)
        self.image = pg.Surface((50, height))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH
        self.rect.bottom = GROUND_Y
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if check_bound_horizontal(self.rect):
            self.kill()

class Coin(pg.sprite.Sprite):
    """
    コイン（黄色い円）に関するクラス
    """
    def __init__(self, speed):
        super().__init__()
        self.image = pg.Surface((30, 30), pg.SRCALPHA)
        pg.draw.circle(self.image, YELLOW, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.left = WIDTH
        self.rect.top = random.randint(300, 430)
        self.speed = speed

    def update(self):
        self.rect.x -= self.speed
        if check_bound_horizontal(self.rect):
            self.kill()

class Score:
    """
    スコアとコイン数を表示するクラス
    """
    def __init__(self):
        self.font = pg.font.SysFont(None, 40)
        self.score_value = 0
        self.coin_value = 0

    def update(self, screen: pg.Surface):
        score_img = self.font.render(f"Score : {self.score_value}", True, BLACK)
        coin_img = self.font.render(f"Coins : {self.coin_value}", True, BLACK)
        screen.blit(score_img, (20, 20))
        screen.blit(coin_img, (20, 60))


class Life:
    """
    ライフ数を表示するクラス
    """
    def __init__(self, num: int):
        self.num = num

    def update(self, screen: pg.Surface):
        font = pg.font.SysFont(None, 40)
        life_img = font.render(f"Life : {self.num}", True, BLACK)
        screen.blit(life_img, (20, 100))

class Beam(pg.sprite.Sprite):
    """
    障害物を破壊する弾
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((20, 6))
        self.image.fill((255, 255, 0))  # 黄色い弾
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 15

    def update(self):
        self.rect.x += self.speed
        if self.rect.left > WIDTH:
            self.kill()


def main():
    pg.display.set_caption("Temple Run Side Scroll (Sprite Ver.)")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    
    # スプライトグループとインスタンスの生成
    bird = Bird((150, GROUND_Y - 40))
    obstacles = pg.sprite.Group()
    coins = pg.sprite.Group()
    beams = pg.sprite.Group()
    score = Score()
    life = Life(3)
    game_over = False
    tmr = 0

    while True:
        key_lst = pg.key.get_pressed()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_r and game_over:
                    score.coin_value -= 10
                    beams.add(Beam(bird.rect.right, bird.rect.centery))
                    # ゲームのリセット（mainを再帰呼び出しせず変数を初期化）
                    main()
                    return
                if event.key == pg.K_l and score.coin_value >= 50 and not game_over:
                    score.coin_value -= 50
                    life.num += 1 #Lキーでライフ回復

        if not game_over:
            # 難易度（速度）の設定
            current_speed = 8 + score.score_value // 10

            # 障害物生成
            if tmr % 60 == 0:
                obstacles.add(Obstacle(current_speed))
            
            # コイン生成
            if tmr % 80 == 0:
                coins.add(Coin(current_speed))

            # 更新
            bird.update(key_lst)
            obstacles.update()
            coins.update()
            beams.update()

            # 衝突判定：コイン（当たったら消える）
            for coin in pg.sprite.spritecollide(bird, coins, True):
                score.coin_value += 1

            # 衝突判定：障害物（当たったらゲームオーバー）
            for obstacle in pg.sprite.spritecollide(bird, obstacles, False):
                if bird.invincible <= 0:      # 無敵時間外ならダメージ
                    life.num -= 1             # ライフを1減らす
                    bird.invincible = 60      # 60フレーム無敵
                if life.num <= 0:         # ライフが0ならゲームオーバー
                     game_over = True

            # 弾と障害物の衝突
            for beam in beams:
                hit_list = pg.sprite.spritecollide(beam, obstacles, True)
                if hit_list:
                    beam.kill()

            # 通過判定（画面外に消えた障害物をスコアに加算）
            for obstacle in obstacles:
                if obstacle.rect.x < -10 and not hasattr(obstacle, "scored"):
                    score.score_value += 1
                    obstacle.scored = True # 重複加算防止フラグ

        # 描画
        screen.fill(SKY) # 背景（空のみ、雲なし）

        # 地面
        pg.draw.rect(screen, GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pg.draw.rect(screen, BROWN, (0, GROUND_Y, WIDTH, 10))

        # 【削除】ここに雲の描画処理がありましたが、削除しました

        # 各オブジェクト描画
        obstacles.draw(screen)
        coins.draw(screen)
        beams.draw(screen)
        screen.blit(bird.image, bird.rect)
        score.update(screen)
        life.update(screen)

        if game_over:
            big_font = pg.font.SysFont(None, 80)
            over_img = big_font.render("GAME OVER", True, RED)
            retry_img = pg.font.SysFont(None, 40).render("Press R to Retry", True, BLACK)
            screen.blit(over_img, (WIDTH//2 - 160, HEIGHT//2 - 40))
            screen.blit(retry_img, (WIDTH//2 - 100, HEIGHT//2 + 40))

        pg.display.update()
        tmr += 1
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()