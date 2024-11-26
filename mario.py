import pygame
import random
import sys

# intialize pygame and pygame mixer for sound
pygame.init()
pygame.mixer.init()

# screen dimensinos
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mario Run | Julien Okumu")

# color definitions
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)

# ground level
ground_level = screen_height - 50

# game clock to control frame rate
clock = pygame.time.Clock()

# power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, power_type):
        super().__init__()

        # different power-up types
        if power_type == 'coin':
            self.image = pygame.image.load('coin.png')
            self.image = pygame.transform.scale(self.image, (30, 30))
            self.power_type = 'coin'

        elif power_type == 'star':
            self.image = pygame.image.load('star.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.power_type = 'star'
        
        # positioning and movement
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.y = random.randint(100, screen_height - 100)
        self.speed = 5

    def update(self):
        # move power-up to the left
        self.rect.x -= self.speed

        # remove power-up when off screen
        if self.rect.right < 0:
            self.kill()

# obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()

        # different obstacle types with unique characteristcs
        if obstacle_type == 'pipe':
            self.image = pygame.image.load('pipemario.png')
            self.image = pygame.transform.scale(self.image, (50, 80))
            self.speed = 5

        elif obstacle_type == 'goomba':
            self.image = pygame.image.load('goomba.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.speed = 6

        # set obstacles rect and positioning
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.bottom = ground_level

        # store obstacle type for specific interaction
        self.obstacle_type = obstacle_type

    def update(self):
        # move obstacle to the left
        self.rect.x -= self.speed

        # remove obstacle when it goes off screen
        if self.rect.right < 0:
            self.kill()

# Mario class
class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # load mario running sprites
        original_sprite = pygame.image.load('mariosprite.png')
        scaled_sprite = pygame.transform.scale(original_sprite, (540, 220))

        # running animation frames
        self.running_frames = [
            scaled_sprite.subsurface((0, 0, 180, 220)),
            scaled_sprite.subsurface((180, 0, 180, 220)),
            scaled_sprite.subsurface((360, 0, 180, 220))
        ]

        # resizing frames
        self.running_frames = [pygame.transform.scale(frame, (60, 80)) for frame in self.running_frames]

        # animation variables
        self.current_frame = 0
        self.animation_timer = 0

        # initial positioning
        self.image = self.running_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.bottom = ground_level

        # advanced jumping mechanics
        self.velocity_y = 0
        self.jump_count = 0 # track number of jumps
        self.max_jumps = 2 # allow double jumping
        self.is_jumping = False
        self.invincibility_timer = 0
        self.is_invincible = False

    def update(self):
        # running animation logic
        self.animation_timer += 1
        if self.animation_timer >= 5:
            self.current_frame = (self.current_frame + 1) % len(self.running_frames)
            self.image = self.running_frames[self.current_frame]
            self.animation_timer = 0

        # gravity simulation
        self.velocity_y += 0.5
        self.rect.y += self.velocity_y

        # ground collision
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.velocity_y = 0
            self.jump_count = 0
            self.is_jumping = False

        # invincibility timer
        if self.is_invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False

    def advanced_jump(self):
        # advanced jumping with double jump
        if self.jump_count < self.max_jumps:
            # jump sound effect
            jump_sound.play()

            # reset vertical velocity and increase jump count
            self.velocity_y = -12
            self.jump_count += 1
            self.is_jumping = True

    def reset(self):
        # reset marios state
        self.rect.x = 100
        self.rect.bottom = ground_level
        self.velocity_y = 0
        self.jump_count = 0
        self.is_jumping = False
        self.current_frame = 0
        self.animation_timer = 0
        self.is_invincible = False

# load sound effects
jump_sound = pygame.mixer.Sound('mariojump.ogg')
jump_sound.set_volume(0.3)
coin_sound = pygame.mixer.Sound('coin.ogg')
coin_sound.set_volume(0.3)
game_over_sound = pygame.mixer.Sound('mariogameover.ogg')
star_sound = pygame.mixer.Sound('star.ogg')

# background music
pygame.mixer.music.load('mariotheme.ogg')
pygame.mixer.music.set_volume(1.0)
pygame.mixer.music.play(-1) # loop indefinetely

# main game function
def main():
    # load background
    background = pygame.image.load('background.png')
    background = pygame.transform.scale(background, (screen_width, screen_height))

    # create sprite groups
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    power_ups = pygame.sprite.Group()

    # create mario
    mario = Mario()
    all_sprites.add(mario)

    # game variables
    score = 0
    coins = 0
    obstacle_spawn_timer = 0
    power_up_spawn_timer = 0
    game_over = False

    # game loop
    running = True
    while running:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    mario.advanced_jump()

                # restart mechanism
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    score = 0
                    coins = 0
                    mario.reset()
                    obstacles.empty()
                    power_ups.empty()

                    # restart background music
                    pygame.mixer.music.play(-1)

        if not game_over:
            # obstacle spawning mechanism
            obstacle_spawn_timer += 1
            if obstacle_spawn_timer >= 60:
                # randomize obstacle types
                obstacle_types = ['pipe', 'goomba']
                obstacle = Obstacle(random.choice(obstacle_types))
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                obstacle_spawn_timer = 0

            # power-up spawning mechanism
            power_up_spawn_timer += 1
            if power_up_spawn_timer >= 120: # spawn powerups less frequently
                power_up_types = ['coin', 'star']
                power_up = PowerUp(random.choice(power_up_types))
                all_sprites.add(power_up)
                power_ups.add(power_up)
                power_up_spawn_timer = 0

            # update game objects
            all_sprites.update()

            # collision detection
            for obstacle in obstacles:
                if mario.rect.colliderect(obstacle.rect) and not mario.is_invincible:
                    game_over = True
                    game_over_sound.play() # play game over sound

            for power_up in power_ups:
                if mario.rect.colliderect(power_up.rect):
                    if power_up.power_type == 'coin':
                        coins += 1
                        coin_sound.play() # play coin sound
                    elif power_up.power_type == 'star':
                        mario.is_invincible = True
                        mario.invincibility_timer = 300 # 5 seconds of invincibility
                        star_sound.play() # play start sound
                    power_up.kill() # remove powerup after collection


            # score tracking
            for obstacle in obstacles:
                if obstacle.rect.right < mario.rect.left:
                    score += 1
        
        # draw everything
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        # score display
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, black)
        coins_text = font.render(f"Coins: {coins}", True, black)
        screen.blit(score_text, (10, 10))
        screen.blit(coins_text, (10, 50))

        # game over screen
        if game_over:
            # stop background music
            pygame.mixer.music.stop()

            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render("Game Over", True, red)
            restart_text = font.render("Press R to Restart", True, black)

            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 -50))
            screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 50))

        # update display
        pygame.display.flip()
        clock.tick(60) # 60fps

    # quit game
    pygame.quit()
    sys.exit()

# entry point
if __name__ == "__main__":
    main()
            

