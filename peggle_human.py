import pygame
import random
import math
import numpy as np
import time
import ctypes

# Only works on Windows
try:
    ctypes.windll.user32.SetProcessDPIAware()
except AttributeError:
    pass

# Constants
WIDTH, HEIGHT = 1200, 1200
FPS = 60
GRAVITY = .22
BALL_RADIUS = 13
BALL_X_START = WIDTH // 2
BALL_Y_START = 30
LAUNCH_VELOCITY = 12
PEG_RADIUS = 20
NUM_PEGS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PEG_COLOR = (255, 0, 0)
DOTTED_LINE_COLOR = (200, 200, 200)

# Ball class
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.radius = BALL_RADIUS

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY  # Gravity

        # Bounce off the sides
        if self.x > WIDTH - self.radius:
            self.x = WIDTH - self.radius
            self.vx *= -0.7 
        if self.x < 0 + self.radius:
            self.x = 0 + self.radius
            self.vx *= -0.7

    def in_bounds(self):
        return self.y < HEIGHT   

    def reset(self):
        self.x = BALL_X_START
        self.y = BALL_Y_START

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)

# Peg class
class Peg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PEG_RADIUS

    def draw(self, screen):
        pygame.draw.circle(screen, PEG_COLOR, (int(self.x), int(self.y)), self.radius)

    def is_colliding(self, ball):
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        return distance < (self.radius + ball.radius)

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Simple Peggle Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        self.balls = 10
        self.ball = Ball(WIDTH // 2, 30)
        self.pegs = [Peg(random.randint(50, WIDTH - 100), random.randint(100, WIDTH-100)) for _ in range(NUM_PEGS)]
        self.is_ball_moving = False
        self.launch_direction = np.pi / 2

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pressed_keys = pygame.key.get_pressed()
        
            if pressed_keys[pygame.K_LEFT]:
                if self.launch_direction < np.pi:
                    self.launch_direction += .01
            elif pressed_keys[pygame.K_RIGHT]:
                if self.launch_direction > 0:
                    self.launch_direction -= .01
            elif pressed_keys[pygame.K_RETURN] and not self.is_ball_moving:
                    self.launch_ball(self.launch_direction)

            self.update()
      
            self.draw()
            self.clock.tick(FPS)

            if (self.balls == 0 and self.is_ball_moving == False) or len(self.pegs) == 0:
                self.draw(game_end=True)
                self.clock.tick()
                pygame.quit()

    def launch_ball(self, direction):
        x_dir = np.cos(direction)
        y_dir = np.sin(direction)
        self.ball.vx = x_dir * LAUNCH_VELOCITY  # Scale velocity
        self.ball.vy = y_dir * LAUNCH_VELOCITY
        self.is_ball_moving = True
        self.balls -= 1

    def update(self):
        if self.is_ball_moving:
            self.ball.update()

            # Check for collisions
            for peg in self.pegs:
                if peg.is_colliding(self.ball):
                    self.handle_collision(peg)
                    break

            if not self.ball.in_bounds():
                self.is_ball_moving = False
                self.ball.reset()


    def handle_collision(self, peg):
        # Calculate the normal vector at the point of collision
        nx = self.ball.x - peg.x
        ny = self.ball.y - peg.y
        norm = math.sqrt(nx ** 2 + ny ** 2)
        nx /= norm  # Normalize
        ny /= norm  # Normalize

        # Reflect the ball's velocity
        dot_product = self.ball.vx * nx + self.ball.vy * ny
        self.ball.vx -= 1.9 * dot_product * nx
        self.ball.vy -= 1.9 * dot_product * ny
        
        # Move the ball outside the peg to prevent sticking
        overlap = self.ball.radius + peg.radius - math.sqrt((self.ball.x - peg.x) ** 2 + (self.ball.y - peg.y) ** 2)
        self.ball.x += nx * overlap
        self.ball.y += ny * overlap
        
        # Optionally remove the peg
        self.pegs.remove(peg)

    def draw_trajectory(self, gravity, velocity_scale):
        # Calculate the initial velocity based on the launch direction radian
        x_dir = np.cos(self.launch_direction)
        y_dir = np.sin(self.launch_direction)

        # Initial velocities based on direction
        initial_vx = x_dir * velocity_scale
        initial_vy = y_dir * velocity_scale

        # Time step for the simulation (this controls how many points we draw)
        time_steps = 50
        time_increment = 1

        # List to store trajectory points
        points = []
        for step in range(time_steps):
            t = step * time_increment
            # Predict the position of the ball at time t
            x = BALL_X_START + initial_vx * t
            y = BALL_Y_START + initial_vy * t + 0.5 * gravity * t ** 2

            # Stop drawing if the trajectory goes below the screen
            if y > HEIGHT:
                break

            points.append((int(x), int(y)))

        # Draw the curved trajectory as small circles along the path
        for point in points:
            pygame.draw.circle(self.screen, DOTTED_LINE_COLOR, point, 3)

    def draw(self, game_end=False):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Balls: " + str(self.balls), True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (70, 20)

        self.screen.fill(BLACK)
        self.ball.draw(self.screen)
        for peg in self.pegs:
            peg.draw(self.screen)

        # Draw the trajectory line if the ball is not moving
        if not self.is_ball_moving:
            self.draw_trajectory(GRAVITY, LAUNCH_VELOCITY)

        self.screen.blit(text, textRect)

        if game_end:
            font2 = pygame.font.Font('freesansbold.ttf', 60)
            text2 = font2.render("Pegs hit: " + str(NUM_PEGS - len(self.pegs)), True, (255, 255, 255))
            textRect2 = text2.get_rect()
            textRect2.center = (WIDTH // 2, HEIGHT // 2)
            self.screen.blit(text2, textRect2)
            pygame.display.flip()
            time.sleep(7)

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    game = Game()
    game.run()
