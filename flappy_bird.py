# Flappy bird where the bird uses NEAT (Neuroevolution of Augmenting Topologies) to learn how to not hit pipes or the ground.
# Author: Tim Turnbaugh
# Last Updated: 12/17/20

import pygame
import neat
import os
import random

# Allows fonts to render (Note: Must be at the top of code)
pygame.font.init()

######################################
# Constants for PyGame
######################################
# Screensize
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

# Object Images
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

# Font for Score and Generation Counter
GAME_FONT = pygame.font.SysFont("Open Sans", 35)

GENERATION = 0

class Bird:
    """Creates a bird object for the player to control"""
    #######################
    # BIRD Constants
    #######################
    IMAGES = BIRD_IMAGES
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Initialize Bird Object
        :param x: starting x position
        :param y: starting y position
        """
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.image_count = 0
        self.image = self.IMAGES[0]

    def jump(self):
        """Allows the Bird to flap its wings/ 'jump' """
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """Used for visual movement of the bird"""
        # Used as game time
        self.tick_count += 1

        # Adjust bird direction
        displacement = self.velocity * self.tick_count + (1.5 * self.tick_count ** 2)

        # Upper limit on vertical speed
        if displacement >= 16:
            displacement = 16

        if displacement < 0:
            displacement -= 2

        # Controls how many pixels the bird moves in the y direction
        self.y = self.y + displacement

        # Adjust tilt of bird if still traveling upward
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            # Adjusts downward tilt up to 90 degrees (Vertical drop)
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        """Controls Bird Flapping/Bird Appearance"""

        # Cycles through bird images in accordance with "frame rate"
        self.image_count += 1
        if self.image_count < self.ANIMATION_TIME * 2:
            self.image = self.IMAGES[0]
        elif self.image_count < self.ANIMATION_TIME * 3:
            self.image = self.IMAGES[2]
        elif self.image_count < self.ANIMATION_TIME * 4:
            self.image = self.IMAGES[1]
        elif self.image_count == self.ANIMATION_TIME * 4 + 1:
            self.image = self.IMAGES[0]
            self.image_count = 0

        # If bird is nose diving there is no flapping
        if self.tilt <= -80:
            self.image = self.IMAGES[1]
            self.image_count = self.ANIMATION_TIME * 2

        # Rotates image with Pygame
        rotated_image = pygame.transform.rotate(self.image, self.tilt)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        """Allows for pixel perfect collision (Ignores transparent pixels on images)"""
        return pygame.mask.from_surface(self.image)


class Pipe:
    """Pipe Class for lateral moving obstacles"""

    #######################
    # Pipe Constants
    #######################
    GAP = 200  # Pipe separation
    VELOCITY = 5  # Horizontal speed

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0

        # Top pipe must be rotated image
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMAGE, False, True)
        self.PIPE_BOTTOM = PIPE_IMAGE

        # If bird has passed the pipe
        self.passed = False
        self.set_height()

    def set_height(self):
        """Assigns pipe object to a random height and adjusts top and bottom pipe heights accordingly to preserve gap size"""
        self.height = random.randrange(50, 450)

        # Adjust where image is drawn on top
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """Moves pipe horizontally toward the left edge of the window"""
        self.x -= self.VELOCITY

    def draw(self, window):
        """Draws upper and lower pipe on screen at their respective heights. Vertical gap size between pipes is constant."""
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        Detects whether or not the bird has collided with either the top or bottom pipe
        :param bird: Bird object
        :return: A boolean corresponding to whether or not the bird image overlaps either pipe image indicating a collision
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        collision_point_bottom = bird_mask.overlap(bottom_mask, bottom_offset)
        collision_point_top = bird_mask.overlap(top_mask, top_offset)

        if collision_point_top or collision_point_bottom:
            return True

        return False


class Ground:
    #######################
    # Ground Constants
    #######################
    VELOCITY = 5  # Same as pipe velocity
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x_start = 0
        self.x_end = self.WIDTH

    def move(self):
        """Controls movement for the ground object"""
        self.x_start -= self.VELOCITY
        self.x_end -= self.VELOCITY

        # Loops ground image with a copy of itself
        if self.x_start + self.WIDTH < 0:
            self.x_start = self.x_end + self.WIDTH
        if self.x_end + self.WIDTH < 0:
            self.x_end = self.x_start + self.WIDTH

    def draw(self, window):
        """Draws ground images back to back allowing for looping in the move method"""
        window.blit(self.IMAGE, (self.x_start, self.y))
        window.blit(self.IMAGE, (self.x_end, self.y))


def draw_window(window, birds, pipes, ground, score, generation):
    """Draws the game window and its contents. (Note: Objects later in the method will be drawn over other objects. i.e. the ground will be drawn over the pipes. """

    window.blit(BACKGROUND_IMAGE, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    ground.draw(window)

    for bird in birds:
        bird.draw(window)


    # Controls Score Display. Score readjusts positioning if it gets too large
    score_text = GAME_FONT.render("Score: " + str(score), True, (255, 255, 255))
    window.blit(score_text, (WINDOW_WIDTH - 10 - score_text.get_width(), 10))

    # Generation Display
    gen_text = GAME_FONT.render("Gen: " + str(generation), True, (255, 255, 255))
    window.blit(gen_text, (10, 10))


    pygame.display.update()


def run(config_path):
    """Initializes NEAT module with config.txt data"""
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    # Creates a population based on config file
    population = neat.Population(config)

    # Prints Generation data to console
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    most_fit = population.run(main, 50)  # This is the most fit bird when the program stops. Can be saved with pickle


# All fitness functions require genomes and config to be passed
def main(genomes, config):
    """Where the game + NEAT gets run"""
    # Generation Counter
    global GENERATION
    GENERATION += 1


    birds = []
    networks = []
    ge = []

    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        networks.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    # Create objects start clock and initialize score
    ground = Ground(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    # For game loop
    run = True

    # Main Game Loop
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # Redundancy
                pygame.quit()
                quit()

        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_index = 1
        else:
            # If no birds left quit the game
            run = False  # Redundancy
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = networks[x].activate((bird.y, abs(bird.y - pipes[pipe_index].height),
                                           abs(bird.y - pipes[pipe_index].bottom)))
            # Tanh >= 0.5
            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        pipe_removal = []
        for pipe in pipes:
            for x, bird in enumerate(birds):

                # If bird collides with a pipe it is removed from the game
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    networks.pop(x)
                    ge.pop(x)


                if not pipe.passed and (pipe.x < bird.x):
                    pipe.passed = True
                    add_pipe = True

            # If pipe is off screen remove pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipe_removal.append(pipe)

            pipe.move()

        # Add new pipe once player passes pipe
        if add_pipe:
            score += 1
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(600))

        # Remove off-screen pipes
        for pipe in pipe_removal:
            pipes.remove(pipe)

        # If bird collides with the ground
        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= ground.y or bird.y < 0:
                birds.pop(x)
                networks.pop(x)
                ge.pop(x)

        # Max score value
        if score > 150:
            run = False  # Redundancy
            break

        ground.move()
        draw_window(window, birds, pipes, ground, score, GENERATION)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_txt_path = os.path.join(local_dir, "config.txt")
    run(config_txt_path)
