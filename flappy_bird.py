import pygame
import neat
import time
import os
import random
# Screen size
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load Sprites
BIRD_IMGS = [
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("images", "bird1.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("images", "bird2.png"))),
    pygame.transform.scale2x(pygame.image.load(
        os.path.join("images", "bird3.png")))
]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("images", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("images", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(
    os.path.join("images", "bg.png")))


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # How much the bird is going to ratate
    ROT_VEL = 20  # Rotation Velocity
    ANIMATION_TIME = 5  # Animation speed

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = - 10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        # self.tick_count simulates vecolity
        d = self.vel * self.tick_count + 1.5*self.tick_count**2
        # Example:
        # self.tick_count = 0 -> d = 0.0 + 0.0 = 0 (0 pixels upwards)
        # self.tick_count = 1 -> d = -10.5 + 1.5 = -9 (9 pixels upwards)
        # self.tick_count = 2 -> d = -21.0 + 6.0 = -15 (15 pixels upwards)
        # self.tick_count = 3 -> d = -31.5 + 13.5 = -18 (18 pixels upwards)
        # self.tick_count = 4 -> d = -42.0 + 24.0 = -18 (18 pixels upwards)
        # self.tick_count = 5 -> d = -52.5 + 37.5 = -15 (15 pixels upwards)
        # self.tick_count = 6 -> d = -63.0 + 54.0 = -9 (9 pixels upwards)
        # self.tick_count = 7 -> d = -73.5 + 73.5 = 0 (0 pixels upwards)

        # limit not accelerating too much when we fall
        if d >= 16:
            d = 16

        # When we jump, jump a litle bit more
        if d < 0:
            d -= 2

        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1

        # Bird Sprite animation - wings flap up and then flap down
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # When the bird falls we don't want to keep flapping its wings
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        # Rotate the image around the center
        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


def draw_window(win, bird):
    # Draw Background
    win.blit(BG_IMG, (0, 0))
    # Draw Bird
    bird.draw(win)
    pygame.display.update()


def main():
    bird = Bird(200, 200)
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)  # 30 Frame per Second at most
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        bird.move()
        draw_window(win, bird)

    pygame.quit()
    quit()


main()
