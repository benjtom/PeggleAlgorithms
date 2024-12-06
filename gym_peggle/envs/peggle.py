import gymnasium as gym
from gymnasium.spaces import Discrete, MultiDiscrete
import pygame
import numpy as np
import math

# Constants
WIDTH, HEIGHT = 1200, 1200
GRAVITY = .22
BALL_RADIUS = 13
LAUNCH_VELOCITY = 12
PEG_RADIUS = 20
BALL_X_START = WIDTH // 2
BALL_Y_START = 30

# Dummy Game class
class DummyGame:
    def __init__(self, pegs, direction):
        self.running = True
        self.ball = Ball(BALL_X_START, BALL_Y_START)
        self.pegs = []
        for peg in pegs:
            self.pegs.append(Peg(peg.getX(), peg.getY()))
        self.is_ball_moving = False
        self.launch_direction = direction
        self.pegs_in_trajectory = 0

    def launch_ball(self):
        self.ball.reset()
        x_dir = np.cos(self.launch_direction)
        y_dir = np.sin(self.launch_direction)
        self.ball.vx = x_dir * LAUNCH_VELOCITY  # Scale velocity
        self.ball.vy = y_dir * LAUNCH_VELOCITY
        self.is_ball_moving = True

    def update(self):           # Returns a boolean indicating whether or not the ball bounced off a peg in this time step
        if self.is_ball_moving:
            self.ball.update()

            # Check for collisions
            for peg in self.pegs:
                if peg.is_colliding(self.ball):
                    self.handle_collision(peg)
                    return True
            return False

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
        
        # Remove the peg
        peg.setCoords(-50, -50) #TODO


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
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getRadius(self):
        return self.radius

# Peg class
class Peg:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = PEG_RADIUS

    def is_colliding(self, ball):
        distance = math.sqrt((self.x - ball.x) ** 2 + (self.y - ball.y) ** 2)
        return distance < (self.radius + ball.radius)
    
    # def is_touching_aim_dot(self, dot_x, dot_y):
    #     distance = math.sqrt((self.x - dot_x) ** 2 + (self.y - dot_y) ** 2)
    #     return distance < (self.radius + BALL_RADIUS)
    
    def setCoords(self, x, y):
        self.x = x
        self.y = y
    
    def getX(self):
        return self.x
    
    def getY(self):
        return self.y
    
    def getRadius(self):
        return self.radius

# Game class
class Game:
    def __init__(self, pegs_hit, pegs, balls, direction):
        self.balls = balls
        self.pegs_hit = pegs_hit
        self.running = True
        self.ball = Ball(BALL_X_START, BALL_Y_START)
        self.pegs = []
        if len(pegs) > 0:
            for i in range(len(pegs)):
                self.pegs.append(Peg(pegs[i][0], pegs[i][1]))
        self.is_ball_moving = False
        self.launch_direction = direction
        self.pegs_in_trajectory = 0
        self.aim_dots = self.get_aim_dots()

    def launch_ball(self):
        self.ball.reset()
        self.balls -= 1
        x_dir = np.cos(self.launch_direction)
        y_dir = np.sin(self.launch_direction)
        self.ball.vx = x_dir * LAUNCH_VELOCITY  # Scale velocity
        self.ball.vy = y_dir * LAUNCH_VELOCITY
        self.is_ball_moving = True

    def change_aim(self, direction):
        self.launch_direction = direction
        self.aim_dots = self.get_aim_dots()

    def update(self):           # Returns a boolean indicating whether or not the ball bounced off a peg in this time step
        if self.is_ball_moving:
            self.ball.update()

            # Check for collisions
            for peg in self.pegs:
                if peg.is_colliding(self.ball):
                    self.handle_collision(peg)
                    return True
            return False

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
        
        # Remove the peg
        peg.setCoords(-50, -50) #TODO
        self.pegs_hit += 1

    def get_num_remaining_pegs(self):
        num_remaining_pegs = len(self.pegs)
        for peg in self.pegs:
            if peg.getX() == -50 and peg.getY() == -50: #TODO
                num_remaining_pegs -= 1
        return num_remaining_pegs

    def get_aim_dots(self):     # Runs the current shot on a copy of the game state to see where the ball will go
        aim_dots = []

        num_peg_bounces = 0

        dummy_game = DummyGame(self.pegs, self.launch_direction)

        dummy_game.launch_ball()

        while dummy_game.ball.in_bounds():
            bounce_occurred = dummy_game.update()
            if bounce_occurred:
                num_peg_bounces += 1
            aim_dots.append([dummy_game.ball.getX(), dummy_game.ball.getY()])
            if num_peg_bounces >= 2:
                break
    
        if num_peg_bounces > 2:
            num_peg_bounces = 2
        self.pegs_in_trajectory = num_peg_bounces
        return aim_dots


class PeggleEnv(gym.Env):

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 10}

    def __init__(self, render_mode=None):
        self.window_size = WIDTH

        self.num_pegs = 30

        temp_pegs = self.np_random.integers(100, WIDTH - 100, size=(self.num_pegs, 2), dtype=int)
        self.game = Game(0, temp_pegs, 10, np.pi/2)

        self.total_miss = False

        # Observations are dictionaries with the agent's and the target's location.
        # Each location is encoded as an element of {0, ..., `size`}^2,
        # i.e. MultiDiscrete([size, size]).
        # self.observation_space = Dict(
        #     {
        #         "pegs": Box(
        #                     low=100,   # Minimum value for each peg
        #                     high=WIDTH - 100,   # Maximum value for each peg
        #                     shape=(self.num_pegs, 2),   # 2 coordinates
        #                     dtype=int  # Use float32 for compatibility
        #                     ),          

        #         "num_balls": Discrete(11),

        #         "aiming_at_peg": Discrete(2)
        #     }
        # )

        self.observation_space = Discrete(3)    # 0 = not aiming at a peg, 1 = aiming at a peg, 2 = bouncing the ball off of one peg into another

        self.action_space = MultiDiscrete([2, 314159])

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        """
        If human-rendering is used, `self.window` will be a reference
        to the window that we draw to. `self.clock` will be a clock that is used
        to ensure that the environment is rendered at the correct framerate in
        human-mode. They will remain `None` until human-mode is used for the
        first time.
        """
        self.window = None
        self.clock = None

    def _get_obs(self):
        # temp_pegs = np.zeros((self.num_pegs, 2), dtype=int)

        # for i in range(len(self.game.pegs)):
        #         temp_pegs[i] = [self.game.pegs[i].getX(), self.game.pegs[i].getY()]

        return self.game.pegs_in_trajectory

    def _get_info(self):
        return {
            "total_miss": self.total_miss,
            "pegs_hit": self.game.pegs_hit
        }

    def reset(self, seed=None, options=None):
        # We need the following line to seed self.np_random
        super().reset(seed=seed)

        temp_pegs = self.np_random.integers(100, WIDTH - 100, size=(self.num_pegs, 2), dtype=int)
        self.game = Game(0, temp_pegs, 10, np.pi/2)

        self.total_miss = False

        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        if len(action) == 1:
            action_type, aiming_discrete = action[0]
        else:
            action_type, aiming_discrete = action

        aiming_float = aiming_discrete / 100000

        pegs_hit = 0

        reward = 0

        self.total_miss = False

        if action_type == 0:     # Aim
            self.metadata["render_fps"] = 30

            self.game.change_aim(aiming_float)      # Change aim direction

            # print(f"Changed aim to {aiming_float}")

            if self.game.pegs_in_trajectory == 0:
                reward += 0
                # print(f"Didn't aim at a peg. +0")
            elif self.game.pegs_in_trajectory == 1:
                reward += 0
                # print(f"Aimed at a peg. +0")
            elif self.game.pegs_in_trajectory == 2:
                reward += 0
                # print(f"Looked to hit two pegs. +0")

            # if self.render_mode == "human":
            #     self._render_frame()

        elif action_type == 1:   # Fire
            self.metadata["render_fps"] = 60

            self.game.change_aim(self.game.launch_direction)     # Keep launch direction the same, but update aim dots and pegs_in_trajctory

            num_pegs_pre_launch = self.game.get_num_remaining_pegs()

            self.game.launch_ball()

            if self.game.pegs_in_trajectory == 0:
                reward -= 4
                self.total_miss = True
            elif self.game.pegs_in_trajectory == 1:
                reward += 1
                # print(f"Shot while aiming at a peg. +1")
            elif self.game.pegs_in_trajectory == 2:
                reward += 3
                # print(f"Went for a bounce shot. +3")

            while self.game.ball.in_bounds():
                self.game.update()
                if self.render_mode == "human":
                    self._render_frame()

            num_pegs_post_launch = self.game.get_num_remaining_pegs()

            pegs_hit = num_pegs_pre_launch - num_pegs_post_launch

            reward += (1 * pegs_hit)
            # print(f"Hit {pegs_hit} pegs. +{pegs_hit}")

            self.game.change_aim(self.game.launch_direction)     # Keep launch direction the same, but update aim dots and pegs_in_trajectory

        # An episode is done if the agent runs out of balls or hits all pegs
        terminated = False
        if (self.game.balls == 0 or self.game.pegs_hit == self.num_pegs):
            terminated = True
        
        observation = self._get_obs()
        info = self._get_info()

        return observation, reward, terminated, False, info


    def render(self):
        if self.render_mode == "rgb_array":
            return self._render_frame()

    def _render_frame(self):
        if self.window is None and self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((self.window_size, self.window_size))
        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((self.window_size, self.window_size))
        canvas.fill((0, 0, 0))

        # First we draw the ball
        ballX = int(self.game.ball.getX())
        ballY = int(self.game.ball.getY())
        ballRadius = int(self.game.ball.getRadius())
        
        pygame.draw.circle(
            canvas,
            (255, 255, 255),
            (ballX, ballY),
            ballRadius
        )

        # Now we draw the pegs
        for peg in self.game.pegs:
            pegX = int(peg.getX())
            pegY = int(peg.getY())
            pegRadius = int(peg.getRadius())
            if pegX > 0 and pegY > 0:
                pygame.draw.circle(
                    canvas,
                    (255, 0, 0),
                    (pegX, pegY),
                    pegRadius
                )

        # Finally, the aim dots
        for point in self.game.aim_dots:
            if 0 < point[0] and point[0] < WIDTH and point[1] < HEIGHT:
                pygame.draw.circle(canvas, (200, 200, 200), point, 3)

        # Show number of balls
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Balls: " + str(self.game.balls), True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (70, 20)
        canvas.blit(text, textRect)

        if self.render_mode == "human":
            # The following line copies our drawings from `canvas` to the visible window
            self.window.blit(canvas, canvas.get_rect())
            pygame.event.pump()
            pygame.display.update()

            # We need to ensure that human-rendering occurs at the predefined framerate.
            # The following line will automatically add a delay to
            # keep the framerate stable.
            self.clock.tick(self.metadata["render_fps"])
        else:  # rgb_array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
