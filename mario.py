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

# colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# ground level
ground_level = screen_height - 50 # adjusted ground level

# game clock to control frame rate
clock = pygame.time.Clock()

# mario class
class Mario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # load mario running sprites with resizing
        original_sprite = pygame.image.load('mariosprite.png')

        # resize the sprite sheet first
        scaled_sprite = pygame.transform.scale(original_sprite, (540, 220))

        # load running frames with smaller dimensions
        self.running_frames = [
            scaled_sprite.subsurface((0, 0, 180, 220)),
            scaled_sprite.subsurface((180, 0, 180, 220)),
            scaled_sprite.subsurface((360, 0, 180, 220))
        ]

        # further resize the frames if needed
        self.running_frames = [pygame.transform.scale(frame, (60, 80)) for frame in self.running_frames]

        # current frame and animation timer
        self.current_frame = 0
        self.animation_timer = 0

        # set initial image and rect
        self.image = self.running_frames[0]
        self.rect = self.image.get_rect()

        # adjust mario's position
        self.rect.x = 100
        self.rect.bottom = ground_level # place mario on the ground
        self.velocity_y = 0
        self.is_jumping = False
    def update(self):
        # animate running frames
        self.animation_timer += 1
        if self.animation_timer >= 5: # change frame every 5 ticks
            self.current_frame = (self.current_frame + 1) % len(self.running_frames)
            self.image = self.running_frames[self.current_frame]
            self.animation_timer = 0

        # apply gravity
        self.velocity_y += 0.5
        self.rect.y += self.velocity_y

        # ground collision
        if self.rect.bottom >= ground_level:
            self.rect.bottom = ground_level
            self.velocity_y = 0
            self.is_jumping = False

    def jump(self):
        # jump only if not already jumping
        if not self.is_jumping:
            self.velocity_y = -12
            self.is_jumping = True

    def reset(self):
        # reset mario's position and state
        self.rect.x = 100
        self.rect.bottom = ground_level
        self.velocity_y = 0
        self.is_jumping = False
        self.current_frame = 0
        self.animation_timer = 0

# pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # load pipe image and resize
        self.image = pygame.image.load('pipemario.png')
        self.image = pygame.transform.scale(self.image, (50, 80)) # adjusted pipe size

        # position pipe at right side of the screen
        self.rect = self.image.get_rect()
        self.rect.x = screen_width
        self.rect.bottom = ground_level + 20 # align pipe with the ground

    def update(self):
        # move pipe to the left
        self.rect.x -= 5

        # remove pipe if off screen
        if self.rect.right < 0:
            self.kill()

# main game loop
# main game loop
def main():
    # load background
    background = pygame.image.load('background.png')
    background = pygame.transform.scale(background, (screen_width, screen_height))

    # create sprite groups
    all_sprites = pygame.sprite.Group()
    pipes = pygame.sprite.Group()

    # create mario
    mario = Mario()
    all_sprites.add(mario)

    # game variables
    score = 0
    pipe_spawn_timer = 0
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
                elif event.key == pygame.K_r and game_over:
                    # restart the game
                    game_over = False
                    score = 0
                    mario.reset()

                    # clear existing pipes
                    pipes.empty()

        if not game_over:
            # spawn pipes
            pipe_spawn_timer += 1
            if pipe_spawn_timer >= 60: # spawn pipe every 60 frames
                pipe = Pipe()
                all_sprites.add(pipe)
                pipes.add(pipe)
                pipe_spawn_timer = 0

            # update sprites
            all_sprites.update()

            # collision detection
            for pipe in pipes:
                if mario.rect.colliderect(pipe.rect):
                    if mario.velocity_y > 0: # mario is falling down
                        if mario.rect.bottom > pipe.rect.top: # if mario's bottom is below the pipe's top
                            game_over = True # trigger game over
                    else: # if mario is jumping
                        if mario.rect.top < pipe.rect.bottom: # if mario's top is above the pipe's bottom
                            # push mario down to the top of the pipe
                            mario.rect.bottom = pipe.rect.top
                            mario.velocity_y = 0 # reset vertical velocity
                        elif mario.rect.right > pipe.rect.left and mario.rect.left < pipe.rect.right:
                            # handle side collision
                            mario.rect.right = pipe.rect.left # push mario away form the pipe

                # score mechanism
                if pipe.rect.right < mario.rect.left:
                    score += 1
                    pipe.kill() # remove pipe after scoring

        # drawing
        screen.blit(background, (0, 0))
        all_sprites.draw(screen)

        # display score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, black)
        screen.blit(score_text, (10, 10))

        # game over screen
        if game_over:
            game_over_font = pygame.font.Font(None, 74)
            game_over_text = game_over_font.render("Game Over", True, red)
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, black)

            screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 -50))
            screen.blit(restart_text, (screen_width // 2 - restart_text.get_width() // 2, screen_height // 2 + 50))

        # update display
        pygame.display.flip()
        clock.tick(60) # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()