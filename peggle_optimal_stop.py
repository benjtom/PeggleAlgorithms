import pygame
import numpy as np
import math
import sys

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

    def change_aim(self, direction, get_aim_dots=True):
        self.launch_direction = direction
        if get_aim_dots:
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
    
    def get_shot_score(self):     # Runs the current shot on a copy of the game state to see where the ball will go
        num_peg_bounces = 0

        dummy_game = DummyGame(self.pegs, self.launch_direction)

        dummy_game.launch_ball()

        while dummy_game.ball.in_bounds():
            bounce_occurred = dummy_game.update()
            if bounce_occurred:
                num_peg_bounces += 1
    
        return num_peg_bounces


# Simulation class
class Simulation:
    def __init__(self, render=True):
        self.render = render
        if render:
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((WIDTH, HEIGHT))
            self.clock = pygame.time.Clock()
            self.canvas = pygame.Surface((WIDTH, HEIGHT))
        temp_pegs = np.random.randint(100, WIDTH - 100, size=(30, 2))
        self.game = Game(0, temp_pegs, 10, np.pi/2)

    def render_frame(self):
        self.canvas.fill((0, 0, 0))

        ballX = int(self.game.ball.getX())
        ballY = int(self.game.ball.getY())
        ballRadius = int(self.game.ball.getRadius())
            
        pygame.draw.circle(
            self.canvas,
            (255, 255, 255),
            (ballX, ballY),
            ballRadius
        )

        for peg in self.game.pegs:
            pegX = int(peg.getX())
            pegY = int(peg.getY())
            pegRadius = int(peg.getRadius())
            if pegX > 0 and pegY > 0:
                pygame.draw.circle(
                    self.canvas,
                    (255, 0, 0),
                    (pegX, pegY),
                    pegRadius
                )

        for point in self.game.aim_dots:
            if 0 < point[0] and point[0] < WIDTH and point[1] < HEIGHT:
                pygame.draw.circle(self.canvas, (200, 200, 200), point, 3)

        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render("Balls: " + str(self.game.balls), True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (70, 20)
        self.canvas.blit(text, textRect)

        self.window.blit(self.canvas, self.canvas.get_rect())
        pygame.event.pump()
        pygame.display.update()

        self.clock.tick(60)

    def run(self, mode):
        if self.render:
            self.render_frame()

        if mode == "random":
            while self.game.balls > 0:
                if self.game.pegs_hit == len(self.game.pegs):
                    break

                self.game.change_aim(np.random.randint(0, 314160)/100000)
                self.game.launch_ball()

                while self.game.ball.in_bounds():
                    self.game.update()
                    if self.render:
                        self.render_frame()

        if mode == "default":
            while self.game.balls > 0:
                if self.game.pegs_hit == len(self.game.pegs):
                    break

                self.game.change_aim(self.get_default_shot())
                self.game.launch_ball()

                while self.game.ball.in_bounds():
                    self.game.update()
                    if self.render:
                        self.render_frame()

        if mode == "perfect":
            while self.game.balls > 0:
                if self.game.pegs_hit == len(self.game.pegs):
                    break

                self.game.change_aim(self.get_perfect_shot())
                self.game.launch_ball()

                while self.game.ball.in_bounds():
                    self.game.update()
                    if self.render:
                        self.render_frame()

        if mode == "optimal-stop":
            while self.game.balls > 0:
                if self.game.pegs_hit == len(self.game.pegs):
                    break

                self.game.change_aim(self.get_optimal_stopping_shot())
                self.game.launch_ball()

                while self.game.ball.in_bounds():
                    self.game.update()
                    if self.render:
                        self.render_frame()

        return self.game.pegs_hit
    

    def get_perfect_shot(self):
        most_pegs_hit = 0
        optimal_aim = 0
        for i in range(0, 3142):
            aiming_float = i / 1000
            self.game.change_aim(aiming_float, False)

            pegs_hit = self.game.get_shot_score()

            if pegs_hit > most_pegs_hit:
                most_pegs_hit = pegs_hit
                optimal_aim = aiming_float

        return optimal_aim
    
    def get_default_shot(self):
        most_pegs_hit = 0
        optimal_aim = 0
        selection_of_shots = np.random.permutation(3142)[:120]

        for shot in selection_of_shots:
            aiming_float = shot / 1000
            self.game.change_aim(aiming_float, False)

            pegs_hit = self.game.get_shot_score()

            if pegs_hit > most_pegs_hit:
                most_pegs_hit = pegs_hit
                optimal_aim = aiming_float

        if (most_pegs_hit == 0):
            print("0 pegs hit this time")

        return optimal_aim
    
    def get_optimal_stopping_shot(self):
        all_possible_shots = np.random.permutation(3142)[:3142]

        threshold_index = math.floor(len(all_possible_shots) * .37)  # TODO: Is lower threshold better?

        pre_threshold_shots = all_possible_shots[:threshold_index]  # Slice from the beginning to threshold
        post_threshold_shots = all_possible_shots[threshold_index:]  # Slice from threshold to the end

        most_pegs_pre_threshold = 0

        backup_shot = 0
        pegs_hit_chosen_shot = 0    

        for shot in pre_threshold_shots:
            aiming_float = shot / 1000
            self.game.change_aim(aiming_float, False)

            pegs_hit = self.game.get_shot_score()
            if pegs_hit > 0:
                backup_shot = aiming_float        # A backup shot that got at least 1 peg so that the bot doesn't just miss (at least not often)
                pegs_hit_chosen_shot = pegs_hit

            if pegs_hit > most_pegs_pre_threshold:
                most_pegs_pre_threshold = pegs_hit

        optimal_stopping_shot = backup_shot
                                              
        for shot in post_threshold_shots:
            aiming_float = shot / 1000
            self.game.change_aim(aiming_float, False)

            pegs_hit = self.game.get_shot_score()

            if (pegs_hit/(most_pegs_pre_threshold+1)) >= .2:   # We want the shot taken to be worse than the optimal shot
                optimal_stopping_shot = aiming_float    
                pegs_hit_chosen_shot = pegs_hit
                break

        # print(f"Most pegs hit pre-threshold: {most_pegs_pre_threshold}")
        # print(f"Pegs hit on chosen shot: {pegs_hit_chosen_shot}")
        if (pegs_hit_chosen_shot == 0):
            print("0 pegs hit this time")

        return optimal_stopping_shot



def main(mode, simulations, render):
    total_pegs_hit = 0
    for i in range(simulations):
        simulation = Simulation(render)
        pegs_hit = simulation.run(mode)
        print(f"{mode} Simulation {i} saw {pegs_hit} pegs get hit.")
        total_pegs_hit += pegs_hit

    print(f"Average number of pegs hit over {simulations} simulations: {total_pegs_hit/simulations}")
    
    
if __name__ == "__main__":
    mode = "optimal-stop"
    simulations = 1
    render = False

    if len(sys.argv) > 1:
        mode = sys.argv[1]
    if len(sys.argv) > 2:
        simulations = int(sys.argv[2])
    if len(sys.argv) > 3:
        if sys.argv[3] == "render" or sys.argv[3] == "true":
            render = True

    main(mode, simulations, render)