import pygame
from settings import PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT, INVINCIBLE_END, PLAYER_MAX_HEALTH, SHOOTING_END, ATTACKING_END, TIME_WARP_DURATION_MS, TIME_WARP_MAX_CHARGES, TIME_WARP_ENEMY_SPEED_MULTIPLIER
from player_skins import load_player_skin
from projectile import Shuriken

class Player(pygame.Rect):
    def __init__(self, player_id=1, spawn_x=PLAYER_X, spawn_y=PLAYER_Y, skin_id="samurai"):
        pygame.Rect.__init__(self,  spawn_x, spawn_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.player_id = player_id
        self.skin_id = skin_id
        self.skin = load_player_skin(skin_id)
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y
        self.image = self.skin["right"]
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.invincible = False
        self.attacking = False
        self.attack_rect = None
        self.attack_damage = 3
        self.shuriken_damge = 2
        self.shooting = False
        self.direction = "right"
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.shurikens = []
        self.score = 0
        self.time_warp_charges = 0
        self.time_warp_active_until = 0
        self.time_warp_duration_ms = TIME_WARP_DURATION_MS
        self.time_warp_max_charges = TIME_WARP_MAX_CHARGES
        self.time_warp_enemy_speed_multiplier = TIME_WARP_ENEMY_SPEED_MULTIPLIER
        self.has_boss_key = False
        self.reached_exit = False
        self.exit_zones = []

    def reset_to_spawn(self):
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.velocity_x = 0
        self.velocity_y = 0
        self.jumping = False
        self.invincible = False
        self.attacking = False
        self.attack_rect = None
        self.shooting = False
        self.shurikens.clear()
        self.reached_exit = False
    
    def update_image(self):
        # if self.jumping:
        #     self.width = PLAYER_JUMP_WIDTH
        #     self.height = PLAYER_JUMP_HEIGHT
        #     if self.direction == "right":
        #         self.image = player_image_jump_right
        #     elif self.direction == "left":
        #         self.image = player_image_jump_left
        # else:
        #     self.width = PLAYER_WIDTH
        #     self.height = PLAYER_HEIGHT
        #     if self.direction == "right":
        #         self.image = player_image_right
        #     elif self.direction == "left":
        #         self.image = player_image_left
        if self.jumping:
            self.image = (
                self.skin["jump_right"]
                if self.direction == "right"
                else self.skin["jump_left"]
            )
        elif self.attacking:
            self.image = (
                self.skin["attack_right"]
                if self.direction == "right"
                else self.skin["attack_left"]
            )
            
        elif self.invincible:
            self.image = (
                self.skin["hit_right"]
                if self.direction == "right"
                else self.skin["hit_left"]
            )
        else:
            self.image = (
                self.skin["right"]
                if self.direction == "right"
                else self.skin["left"]
            ) 
        
            
    def set_invincible(self, miliseconds = 1000):
        self.invincible = True
        self.update_image()
        self.velocity_x = 0
        self.velocity_y = 0
        pygame.time.set_timer(INVINCIBLE_END, miliseconds) #event called, milliseconds, repeatitions
        
    def set_attack(self):
        if not self.attacking:
            self.attacking = True
            pygame.time.set_timer(ATTACKING_END, 250, 1)   
    
    def set_shooting(self, player):
        if not self.shooting:
            self.shooting = True
            self.shurikens.append(Shuriken(player))
            pygame.time.set_timer(SHOOTING_END, 250, 1)
            
    def set_attack(self):
        if not self.attacking:
            self.attacking = True
            
            attack_width = 40
            attack_height = self.height

            if self.direction == "right":
                self.attack_rect = pygame.Rect(
                    self.right,
                    self.y,
                    attack_width,
                    attack_height
                )
            else:
                self.attack_rect = pygame.Rect(
                    self.x - attack_width,
                    self.y,
                    attack_width,
                    attack_height
                )

            pygame.time.set_timer(ATTACKING_END, 250, 1)

    def add_time_warp_charge(self, max_charges=None):
        cap = self.time_warp_max_charges if max_charges is None else max_charges
        self.time_warp_charges = min(cap, self.time_warp_charges + 1)

    def activate_time_warp(self, duration_ms=None):
        if self.time_warp_charges <= 0:
            return False
        now = pygame.time.get_ticks()
        if now < self.time_warp_active_until:
            return False

        duration = self.time_warp_duration_ms if duration_ms is None else duration_ms
        self.time_warp_charges -= 1
        self.time_warp_active_until = now + duration
        return True

    def is_time_warp_active(self):
        return pygame.time.get_ticks() < self.time_warp_active_until
# left(x), top(y), width, height
# player = Player()

# def draw_player(window, player):
#     window.blit(player.image, player)
    
