# Flappy bird where the bird uses NEAT (Neuroevolution of Augmenting Topologies) to learn how to not hit pipes or the ground.
# Author: Tim Turnbaugh
# Last Updated: 12/17/20

import pygame
import neat
import time
import os
import random

# Allows fonts to render (Note: Must be at the top of code)
pygame.font.init()

######################################
# Constants for PyGame
######################################
# Screensize
WIN_WIDTH = 500
WIN_HEIGHT = 800

# 3 Images of Bird to mimic flapping.
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BACKGROUND_IMAGE = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

SCORE_FONT = pygame.font.SysFont("Times New Roman", 50)




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
        self.height = random.randrange(50, 450)

        # Adjust where image is drawn on top
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """Moves Pipe Horizontally Across the window"""
        self.x -= self.VELOCITY

    def draw(self, window):
        """Draws pipe on screen"""
        window.blit(self.PIPE_TOP, (self.x, self.top))
        window.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        """
        Detects whether or not the bird has collided with either the top or bottom pipe
        :param bird: Bird object
        :return: A boolean corresponding to whether or not the bird image overlaps either pipe image
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
    VELOCITY = 5  # Same as pipe speed
    WIDTH = BASE_IMAGE.get_width()
    IMAGE = BASE_IMAGE

    def __init__(self, y):
        self.y = y
        self.x_start = 0
        self.x_end = self.WIDTH

    def move(self):
        """Controls movement for the ground object"""
        # Ground moves at same velocity as pipes
        self.x_start -= self.VELOCITY
        self.x_end -= self.VELOCITY

        # Loops ground image
        if self.x_start + self.WIDTH < 0:
            self.x_start = self.x_end + self.WIDTH
        if self.x_end + self.WIDTH < 0:
            self.x_end = self.x_start + self.WIDTH

    def draw(self, window):
        """Draws ground images back to back allowing for looping in the move method"""
        window.blit(self.IMAGE, (self.x_start, self.y))
        window.blit(self.IMAGE, (self.x_end, self.y))


def draw_window(window, bird, pipes, ground, score):
    """Draws the game window and its contents (Pipes, bird, ground, score)"""
    window.blit(BACKGROUND_IMAGE, (0, 0))

    for pipe in pipes:
        pipe.draw(window)

    text = SCORE_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    ground.draw(window)

    bird.draw(window)
    pygame.display.update()


def main():
    """Where the game gets run"""
    # Create objects start clock and initialize score
    bird = Bird(230, 350)
    ground = Ground(730)
    pipes = [Pipe(700)]
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        bird.move()

        add_pipe = False
        pipe_removal = []

        for pipe in pipes:
            if pipe.collide(bird):
                pass

            # If pipe is off screen remove pipe
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                pipe_removal.append(pipe)

            # If bird has passed pipe
            if not pipe.passed and (pipe.x < bird.x):
                pipe.passed = True
                add_pipe = True

            pipe.move()

        # Add new pipe once player passes pipe
        if add_pipe:
            score += 1
            pipes.append(Pipe(700))

        # Remove off-screen pipes
        for pipe in pipe_removal:
            pipes.remove(pipe)

        # If bird collides with the ground
        if bird.y + bird.image.get_height() >= ground.y:
            pass

        ground.move()
        draw_window(window, bird, pipes, ground, score)

    pygame.quit()
    quit()


main()
