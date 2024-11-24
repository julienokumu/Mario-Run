# import libraries
import pygame
import random
import sys

# initialize pygame
pygame.init()

# screen dimensions
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Mario Run | Julien Okumu")

# color definitions
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# ground level 
ground_level = screen_height - 50

# game clock to control frame rate
clock = pygame.time.Clock()

# obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, obstacle_type):
        super().__init__()

        # different obstacle types with unique characteristics
        if obstacle_type == 'pipe':
            # load and scale pipe image
            self.image = pygame.image.load('pipemario.png')
            self.image = pygame.transform.scale(self.image, (50, 80))
            self.speed = 5 # standard pipe speed

        elif obstacle_type == 'goomba':
            # load and scale goomba image
            self.image = pygame.image.load('goomba.png')
            self.image = pygame.transform.scale(self.image, (40, 40))
            self.speed = 6 # slightly faster movement

       # elif obstacle_type == 'koopa':
            # load and scale koopa image
           # self.image = pygame.image.load('koopa.png')
            # self.image = pygame.transform.scale(self.image, (50, 50))
           # self.speed = 4 # slower but potentially more challenginf

        # set obstacles rect and positioning
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.bottom = ground_level

        # store obstacle type for specific intercation
        self.obstacle_type = obstacle_type
    
    def update(self):
        # move obstacle to the left
        self.rect.x -= self.speed

        # remove obstacle when it goes off screen
        if self.rect.right < 0:
            self.kill()
# mario class
class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # load mario running sprites with resizing
        original_sprite = pygame.image.load('mariosprite.png')
        scaled_sprite = pygame.transform.scale(original_sprite, (540, 220))

        # running animation frames
        self.running_frames = [
            scaled_sprite.subsurface((0, 0, 180, 220)),
            scaled_sprite.subsurface((180, 0, 180, 220)),
            scaled_sprite.subsurface((360, 0, 180, 220))
        ]

        # resize frames
        self.running_frames = [pygame.transform.scale(frame, (60, 80)) for frame in self.running_frames]

        # animation varibales
        self.current_frame = 0
        self.animation_timer = 0

        # initial positioning
        self.image = self.running_frames[0]
        self.rect  = self.image.get_rect()
        self.rect.x = 100
        self.rect.bottom = ground_level

        # physics varibles
        self.velocity_y = 0
        self.is_jumping = False

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
            self.is_jumping = False

    def jump(self):
        # jump mechanics
        if not self.is_jumping:
            self.velocity_y = -12
            self.is_jumping = True

    def reset(self):
        # reset mario's state
        self.rect.x = 100
        self.rect.bottom = ground_level
        self.velocity_y = 0
        self.is_jumping = False
        self.current_frame = 0
        self.animation_timer = 0

# main game function
def main():
    # load background
    background = pygame.image.load('background.png')
    background = pygame.transform.scale(background, (screen_width, screen_height))

    # create sprite groups
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # create mario
    mario = Mario()
    all_sprites.add(mario)

    # game variables
    score = 0
    obstacle_spawn_timer = 0
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
                    mario.jump()

                # restart mechanism
                if event.key == pygame.K_r and game_over:
                    game_over = False
                    score = 0
                    mario.reset()
                    obstacles.empty()

        if not game_over:
            # obstacle spawning mechanism
            obstacle_spawn_timer += 1
            if obstacle_spawn_timer >= 60:
                # randomize obstacle types
                obstacle_types = ['pipe', 'goomba'] # add 'koopa' if needed
                obstacle = Obstacle(random.choice(obstacle_types))
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                obstacle_spawn_timer = 0

            # update gamme objects
            all_sprites.update()

            # collision detection
            for obstacle in obstacles:
                if mario.rect.colliderect(obstacle.rect):
                    game_over = True

                # score tracking
                if obstacle.rect.right < mario.rect.left:
                    score += 1
                    obstacle.kill()

        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        # score display
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, black)
        screen.blit(score_text, (10, 10))

        # game over screen
        if game_over:
            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render("Game Over", True, red)
            restart_text = font.render("Press R to Restart", True, black)

            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 50))
            screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 50))

        # update display
        pygame.display.flip()
        clock.tick(60) # 60FPS

    # quit game
    pygame.quit()
    sys.exit()

# entry point
if __name__ == "__main__":
    main()