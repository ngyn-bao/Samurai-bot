import pygame
from settings import INFANTRYMAN_WIDTH, INFANTRYMAN_HEIGHT, TILE_SIZE, DRONE_WIDTH, DRONE_HEIGHT, DRONE_VELOCITY_X, DRONE_VELOCITY_Y, INFANTRYMAN_BULLET_VELOCITY_X, INFANTRYMAN_BULLET_VELOCITY_Y, METALL_WIDTH, METALL_HEIGHT,INFANTRYMAN_VELOCITY_X
from images import infantryman_image_left, infantryman_image_right, infantryman_guard_left, infantryman_guard_right, drone_image_left, drone_image_right, infantryman_guard_right2, infantryman_guard_left2, infantryman_image_right2, infantryman_image_left2, boss_spider_image
from projectile import Bullet, Bullet2, ShockWave

class Metall(pygame.Rect): 
    def __init__(self, x, y):
        pygame.Rect.__init__(self, x, y, METALL_WIDTH, METALL_HEIGHT)
        self.image = infantryman_image_left
        self.velocity_y = 0
        self.direction = "left"
        self.jumping = False
        self.health = 4
        self.bullets = []
        self.shooting = False
        self.last_fired = pygame.time.get_ticks() #time in ms after pygame.initialize
        self.aggro_started_at = 0
        self.guarding = False
        self.melee_safe_range = int(TILE_SIZE * 1.7)
        self.shoot_range = int(TILE_SIZE * 4.2)
        self.shoot_cooldown_ms = 850
        self.reaction_delay_ms = 300
        
    def update_image(self):
        if self.direction == "right":
            if self.guarding:
                self.image = infantryman_guard_right
            else:
                self.image = infantryman_image_right
        elif self.direction == "left":
            if self.guarding:
                self.image = infantryman_guard_left
            else:
                self.image = infantryman_image_left

    def set_shooting(self, player, enemy):
        distance = abs(self.x - player.x)

        if distance <= self.melee_safe_range:
            self.guarding = True
            self.aggro_started_at = 0
            return

        self.guarding = False
        if distance <= self.shoot_range:
            now = pygame.time.get_ticks()
            if self.aggro_started_at == 0:
                self.aggro_started_at = now
                return

            if now - self.aggro_started_at < self.reaction_delay_ms:
                return

            if now - self.last_fired > self.shoot_cooldown_ms:
                self.last_fired = now
                self.shooting = True
                self.bullets.append(Bullet(enemy, -INFANTRYMAN_BULLET_VELOCITY_Y))
                self.bullets.append(Bullet(enemy, 0))
                self.bullets.append(Bullet(enemy, INFANTRYMAN_BULLET_VELOCITY_Y))
        else:
            self.guarding = True
            self.aggro_started_at = 0

class Drone(pygame.Rect):
    def __init__(self, x, y):
        pygame.Rect.__init__(self, x, y, DRONE_WIDTH, DRONE_HEIGHT)
        self.image = drone_image_right
        self.direction = "right"
        self.health = 4
        self.velocity_x = DRONE_VELOCITY_X
        self.velocity_y = DRONE_VELOCITY_Y
        self.start_x = x
        self.start_y = y
        self.max_range_x = TILE_SIZE * 5
        self.max_range_y = TILE_SIZE 
        self.state = "patrol"
        self.attack_speed = 7
        self.cooldown_time = 700
        self.last_action_time = 0
        self.attack_range = TILE_SIZE * 6
    def update_image(self):
        if self.direction == "left":
            self.image = drone_image_left
        elif self.direction == "right":
            self.image = drone_image_right
            
class Infantryman(pygame.Rect): 
    def __init__(self, x, y):
        pygame.Rect.__init__(self, x, y, INFANTRYMAN_WIDTH, INFANTRYMAN_HEIGHT)
        self.image = infantryman_image_left2
        self.velocity_y = 0
        self.direction = "left"
        self.jumping = False
        self.health = 6
        self.velocity_x = INFANTRYMAN_VELOCITY_X
        self.start_x = x
        self.max_range_x = TILE_SIZE * 4
        self.bullets = []
        self.shooting = False
        self.last_fired = pygame.time.get_ticks() #time in ms after pygame.initialize
        self.state = "patrol"
    
    def update_image(self):
        if self.direction == "right":
            if self.state == "patrol":
                self.image = infantryman_guard_right2
            else:
                self.image = infantryman_image_right2
        elif self.direction == "left":
            if self.state == "patrol":
                self.image = infantryman_guard_left2
            else:
                self.image = infantryman_image_left2

    def set_shooting(self, player, enemy):
        if abs(self.x - player.x) <= TILE_SIZE * 4:
            now = pygame.time.get_ticks()
            if now - self.last_fired > 750:
                self.last_fired = now
                self.shooting = True
                self.bullets.append(Bullet2(enemy))
                # self.bullets.append(Bullet(enemy, 0))
                # self.bullets.append(Bullet(enemy, INFANTRYMAN_BULLET_VELOCITY_Y))


class SpiderBoss(pygame.Rect):
    def __init__(self, x, y):
        super().__init__(x, y, 96, 96)
        self.max_health = 36
        self.health = self.max_health
        self.image = pygame.transform.smoothscale(boss_spider_image, (self.width, self.height))
        self.start_x = x
        self.ceiling_y = 16
        self.ground_y = 16 + TILE_SIZE * 9

        self.ceiling_speed = 2
        self.drop_speed = 9
        self.climb_speed = 7
        self.direction = 1
        self.patrol_range = TILE_SIZE * 6

        self.state = "intro_descend"
        self.intro_speed = 3

        self.last_action = pygame.time.get_ticks()
        self.attack_cooldown = 1450
        self.ground_wait = 1600

        # telegraph
        self.aim_time = 430       # boss canh theo player truoc khi roi
        self.pre_drop_time = 250  # đứng im cảnh báo
        self.aim_speed = 3
        self.lock_x = None

        self.projectiles = []
        self.has_landed_wave = False
        self.hurt_cooldown_ms = 120
        self.last_hurt_time = 0
    
    def on_hit(self, damage, player):
        now = pygame.time.get_ticks()
        if now - self.last_hurt_time < self.hurt_cooldown_ms:
            return

        self.last_hurt_time = now
        self.health = max(0, self.health - damage)

        # Bị hit thì leo lên ngay (nếu chưa chết)
        if self.health > 0:
            self.state = "climb_back"
            self.has_landed_wave = False
            self.last_action = now
        else:
            player.score += 1500
            
    def _enraged(self):
        return self.health <= self.max_health // 2

    def _update_projectiles(self, speed_scale=1.0):
        for p in self.projectiles:
            p.update(speed_scale)
        self.projectiles[:] = [p for p in self.projectiles if p.alive]

    def move_on_ceiling(self, speed_scale=1.0):
        speed = self.ceiling_speed + (1 if self._enraged() else 0)
        self.x += speed * self.direction * speed_scale
        if self.x <= self.start_x - self.patrol_range:
            self.x = self.start_x - self.patrol_range
            self.direction = 1
        elif self.x >= self.start_x + self.patrol_range:
            self.x = self.start_x + self.patrol_range
            self.direction = -1

    def update(self, player, speed_scale=1.0):
        now = pygame.time.get_ticks()
        self._update_projectiles(speed_scale)

        if self.state == "intro_descend":
            self.y += self.intro_speed
            if self.y >= self.ceiling_y:
                self.y = self.ceiling_y
                self.state = "ceiling_patrol"
                self.last_action = now
            return

        if self.state == "ceiling_patrol":
            self.move_on_ceiling(speed_scale)
            if now - self.last_action >= self.attack_cooldown:
                self.state = "aim_lock"
                self.last_action = now
                self.lock_x = player.centerx - self.width // 2

        elif self.state == "aim_lock":
            # canh từ từ -> player có thời gian đọc chiêu
            if self.x < self.lock_x:
                self.x += min(self.aim_speed * speed_scale, self.lock_x - self.x)
            elif self.x > self.lock_x:
                self.x -= min(self.aim_speed * speed_scale, self.x - self.lock_x)

            if now - self.last_action >= self.aim_time:
                self.state = "pre_drop"
                self.last_action = now

        elif self.state == "pre_drop":
            # đứng im cảnh báo ngắn trước khi rơi
            if now - self.last_action >= self.pre_drop_time:
                self.state = "drop_attack"

        elif self.state == "drop_attack":
            # rơi THẲNG đứng, không track ngang nữa
            self.y += (self.drop_speed + (1 if self._enraged() else 0)) * speed_scale
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.state = "ground_attack"
                self.last_action = now
                self.has_landed_wave = False

        elif self.state == "ground_attack":
            if not self.has_landed_wave:
                self.projectiles.append(ShockWave(self.centerx, self.bottom - 20, 1))
                self.projectiles.append(ShockWave(self.centerx, self.bottom - 20, -1))
                self.has_landed_wave = True

            if now - self.last_action >= self.ground_wait:
                self.state = "climb_back"

        elif self.state == "climb_back":
            self.y -= (self.climb_speed + (1 if self._enraged() else 0)) * speed_scale
            if self.y <= self.ceiling_y:
                self.y = self.ceiling_y
                self.state = "ceiling_patrol"
                self.last_action = now