import pygame
from settings import PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT, INVINCIBLE_END, PLAYER_MAX_HEALTH, SHOOTING_END, ATTACKING_END
from images import player_image_right, player_image_left, player_image_jump_left, player_image_jump_right, player_image_attack_right,player_image_attack_left, player_takehit_left, player_takehit_right
from projectile import Shuriken

class Player(pygame.Rect):
    def __init__(self):
        pygame.Rect.__init__(self,  PLAYER_X, PLAYER_Y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.image = player_image_right
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
        self.has_boss_key = False
        self.reached_exit = False
        self.exit_zones = []
    
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
                player_image_jump_right
                if self.direction == "right"
                else player_image_jump_left
            )
        elif self.attacking:
            self.image = (
                player_image_attack_right
                if self.direction == "right"
                else player_image_attack_left
            )
            
        elif self.invincible:
            self.image = (
                player_takehit_right
                if self.direction == "right"
                else player_takehit_left
            )
        else:
            self.image = (
                player_image_right
                if self.direction == "right"
                else player_image_left
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

    def add_time_warp_charge(self, max_charges):
        self.time_warp_charges = min(max_charges, self.time_warp_charges + 1)

    def activate_time_warp(self, duration_ms):
        if self.time_warp_charges <= 0:
            return False
        now = pygame.time.get_ticks()
        if now < self.time_warp_active_until:
            return False

        self.time_warp_charges -= 1
        self.time_warp_active_until = now + duration_ms
        return True

    def is_time_warp_active(self):
        return pygame.time.get_ticks() < self.time_warp_active_until
# left(x), top(y), width, height
# player = Player()

# def draw_player(window, player):
#     window.blit(player.image, player)
    
