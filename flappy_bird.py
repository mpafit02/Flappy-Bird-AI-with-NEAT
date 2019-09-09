import pygame
import neat
import time
import os
import random
import pickle
pygame.font.init()

GEN = 0

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

STAT_FONT = pygame.font.SysFont("comicsans", 50)


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


class Pipe:
    GAP = 200
    VEL = 5

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        # Flip the pipe image for the top pipes
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
        # Bottom pipes image
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top-round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # checks if thay collide
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        # If one of them is not None we have collision
        if t_point or b_point:
            return True
        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        # Cycle between the two bases when they move out of the screen
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    # Draw the Background
    win.blit(BG_IMG, (0, 0))

    # Draw the Pipes
    for pipe in pipes:
        pipe.draw(win)

    # Draw the Score Shadow
    text = STAT_FONT.render("Score: " + str(score), 1, (0, 0, 0))
    win.blit(text, (WIN_WIDTH - 9 - text.get_width(), 11))

    # Draw the Score
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    # Draw the Generation Shadow
    text = STAT_FONT.render("Gen: " + str(gen), 1, (0, 0, 0))
    win.blit(text, (11, 11))

    # Draw the Generation
    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 30, 30))
    win.blit(text, (10, 10))

    # Draw the Base
    base.draw(win)

    # Draw the Bird
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    # Three parrallel lists where the position i is the data for the ith bird
    nets = []
    ge = []
    birds = []

    for genome_id, genome in genomes:
        # start with fitness level of 0
        genome.fitness = 0
        # Setup a neural network
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        # Create the bird
        birds.append(Bird(230, 350))
        # Create a genome for the specific bird
        ge.append(genome)

    base = Base(730)
    pipes = [Pipe(600)]

    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True
    while run:
        clock.tick(30)  # 30 Frame per Second at most
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            # Move birds
            bird.move()
            # Motivate the birds to move
            ge[x].fitness += 0.1
            # Bird jump if the activation function is greater than 0.5
            output = nets[x].activate((bird.y, abs(
                bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        remove_pipe = []
        add_pipe = False
        for pipe in pipes:

            pipe.move()

            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    # Lose one point because it hitted a pipe
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                remove_pipe.append(pipe)

        if add_pipe:
            score += 1
            # Reward the bird if it passed a pipe
            for g in ge:
                g.fitness += 5
            # Create a new Pipe
            pipes.append(Pipe(600))

        # Remove all the pipes in the remove_pipe list
        for r in remove_pipe:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            # if we touched the ground
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
                ge[x].fitness -= 1
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, GEN)
        # break if score gets large enough
        if score > 20:
            pickle.dump(nets[0], open("best.pickle", "wb"))
            break


def run(config_path):
    # Load the configuration file
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    # Crete a population
    p = neat.Population(config)

    # Print Statistics in CMD
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Generations for the neat function, call the main function 50 times
    winner = p.run(main, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == "__main__":
    # Find the local directory
    local_dir = os.path.dirname(__file__)
    # Load the configuration file
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
