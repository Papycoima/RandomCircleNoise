
# algorithm that generates terrain-like heightmaps
# imagined by me, Daniele Chirico, July 15, 2024

# -----Island Version----- #

# -----Process----- #
# start with a flat heightmap filled with a base terrain height
# select a random point in that heightmap
# take a random offset value, positive or negative
# create a circle with a large enough radius that creates a hole or a bulge as tall as the offset
# select points near the edge of the circe (points that belong to the "domain")
# repeat process

# -----Tile-ability-----#
# at the moment it's not very tile-able as it's iterative, kinda like the square-diamond
# I found a way to make it tile-able, it's just not very simple to implement
# Since a single tile is generated as the surface of a torus, it can tile itself indefinitely
# So you can iterate the same tile and just change the edge that's the furthest away from the edge in common
# if the opposite edge gets modified, you can just mirror the newly generated tile about that edge to create a new tile that tiles in a similar fashion
# or mirror, add a gradient of influence and re-simulate

# -----Details----- #
# radii should get smaller with each iteration (or not, depending on which one creates a better result)
# number of circles should increase with each iteration
# offset should get smaller with each iteration - I find that keeping the offset constant makes for a better result

# -----Requirements----- #
# has to be perfectly tilable
# has to be somewhat fast (100x100 map with 100 radius and 10 generation takes approximately 12 seconds to generate)
# has to rely on some seed (same seed = same heightmap)


# precompute_gradients basically just calculates gradients for each and every radius that would be generated just once.
# in the higher iterations, instead of calculating the same gradient many, many times it just calculates it once and paste it all over

# generate island with one central mountain. One original tile, 8 gradient tiles.
import numpy as np
import random
import matplotlib.pyplot as plt
import math
from PIL import Image


def fading_gradient(size):
    blank = np.full((size, size), 1, dtype=float)
    for x in range(size):
        for y in range(size):
            value = (size - y) / size
            blank[x, y] = value
    return blank


def rising_gradient(size):
    blank = np.full((size, size), 0, dtype=float)
    for x in range(size):
        for y in range(size):
            value = y / size
            blank[x, y] = value
            # value = y / size
            # blank[x, y] = value
    return blank


def precompute_gradients(size):
    gradients = []
    for i in range(0, 9):
        gradient = np.full((size, size), 0, dtype=float)
        for x in range(size):
            for y in range(size):
                if i == 0:
                    distance = math.sqrt(((x - size) ** 2) + ((y - size) ** 2))
                    if distance <= radius:
                        strenght = (1 - (distance / radius))
                        gradient[x, y] = strenght
                if i == 1:
                    value = x / size
                    gradient[x, y] = value
                if i == 2:
                    distance = math.sqrt(((x-size) ** 2) + (y ** 2))
                    if distance <= radius:
                        strenght = (1 - (distance / radius))
                        gradient[x, y] = strenght
                if i == 3:
                    value = y / size
                    gradient[x, y] = value
                if i == 4:
                    value = 1
                    gradient[x, y] = value
                if i == 5:
                    value = (size - y) / size
                    gradient[x, y] = value
                if i == 6:
                    distance = math.sqrt(((x) ** 2) + ((y - size) ** 2))
                    if distance <= radius:
                        strenght = (1 - (distance / radius))
                        gradient[x, y] = strenght
                if i == 7:
                    value = (size - x) / size
                    gradient[x, y] = value
                if i == 8:
                    distance = math.sqrt((x ** 2) + (y ** 2))
                    if distance <= radius:
                        strenght = (1 - (distance / radius))
                        gradient[x, y] = strenght
        gradients.append(gradient)
    return gradients


def precompute_circles(radius, iterations, offset):
    circles = {}
    for i in range(0, iterations):
        flip = random.choice((-1, 1))
        offset *= flip
        radius = radius - (i // iterations)
        circle = np.full((2 * radius + 1, 2 * radius + 1), 0, dtype=float)
        for dx in range(-int(radius), int(radius) + 1):
            for dy in range(-int(radius), int(radius) + 1):
                distance = np.sqrt((dx ** 2) + (dy ** 2))
                if distance <= radius:
                    strenght = (1 - (distance/radius)) * offset
                    circle[dx + radius, dy + radius] += strenght
        circles[i] = circle
    return circles


def generate_tilemap(size, radius, domain_offset, iterations, circles):
    tilemaps = {}
    gradients = precompute_gradients(tile_size)
    main_tile = generate_heightmap(size, radius, domain_offset, iterations, circles)
    for i in range(0, 9):
        tilemap = main_tile * gradients[i]
        tilemaps[i] = tilemap
    return tilemaps


def generate_heightmap(size, radius, domain_offset, iterations, gradients):
    # initializing the heightmap with a base terrain height
    heightmap = np.full((size, size), 255, dtype=float)

    # midpoint of the map
    halfsize = [size // 2, size // 2]

    # i = index of iteration (which iteration it's simulating rn)
    for i in range(iterations):
        for j in range(i):  # more iterations = more points generated  j = number of circles per iteration
            x = random.randint(halfsize[0] - domain_offset, halfsize[0] + domain_offset)
            y = random.randint(halfsize[1] - domain_offset, halfsize[1] + domain_offset)

            gradient = gradients[i]

            # apply gradients
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    heightmap[(x + dx) % size, (y + dy) % size] += gradient[dx + radius, dy + radius]

            halfsize[0] = x
            halfsize[1] = y
            domain_offset = radius
            radius = radius - (i // iterations)

            # radius = radius - int(1/(i+1))
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    heightmap = (heightmap - min_height) / (max_height - min_height) * 255
    return heightmap


def merge_tiles(tile1, tile2, gradient1, gradient2):
    # merge two tiles by applying opposing gradients
    new_tile1 = tile1 * gradient1

    new_tile2 = tile2 * gradient2

    new_tile = new_tile1 + new_tile2

    # plotting the tiles before and after the gradients for debug

    test_tiles = [tile1, new_tile1, gradient1, new_tile2, tile2, gradient2, new_tile]
    fig, axes = plt.subplots(1, len(test_tiles), figsize=(12, 6))
    for i in range(len(test_tiles)):
        axes[i].imshow(test_tiles[i], cmap='terrain')
        axes[i].set_title(f'{seed * (i + i)}')
        axes[i].axis('off')

    plt.tight_layout()
    fig.subplots_adjust(wspace=0)
    plt.show()
    return new_tile


tile_size = 100  # size of the map
base_height = np.full((tile_size, tile_size), 255, dtype=float)  # initial height of the map
radius = 100  # initial radius of the circle around the chosen point (has to be at least half of the tile size) larger values = smaller features = wider view
offset = 20  # how much you want to dig down or bring up (negative numbers have better results
domain_offset = tile_size // 2  # how close should the next-gen circles be from the first. It is initialized as half the map so the whole map is a candidate for the firs point
iterations = 10  # how many generations to compute (low values make for crisper lines, high values make for more fractal-like appearance
seed = 4578  # seed of the random number generator

random.seed(seed)
np.random.seed(seed)

circles = precompute_circles(radius, iterations, offset)
tilemap = generate_tilemap(tile_size, radius, domain_offset, iterations, circles)

name = random.randint(0, 100000)

fig, axes = plt.subplots(3, 3, figsize=(6, 6))
for x in range(3):
    for y in range(3):
        axes[x, y].imshow(tilemap[(3 * x) + y], cmap='terrain', vmin=0, vmax=255)
        axes[x, y].axis('off')

plt.tight_layout()
fig.subplots_adjust(hspace=0)
fig.subplots_adjust(wspace=0)
plt.show()
