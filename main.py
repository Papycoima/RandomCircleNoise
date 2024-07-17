
# algorithm that generates terrain-like heightmaps
# imagined by me, Daniele Chirico, July 15, 2024

import numpy as np
import random
import matplotlib.pyplot as plt
from PIL import Image

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

def precompute_gradients(radius, iterations, offset):
    gradients = {}
    # flip = random.choice((-1, 1))  # to choose if the offset will dig down or bring up the terrain
    offset = offset * -1
    for i in range(0, iterations):
        gradients[i] = []
        radius = radius - int(i / iterations)
        gradient = np.full((2 * radius + 1, 2 * radius + 1), 0, dtype=float)

        for dx in range(-int(radius), int(radius) + 1):
            for dy in range(-int(radius), int(radius) + 1):
                distance = np.sqrt((dx ** 2) + (dy ** 2))
                if distance <= radius:
                    strenght = (1 - (distance/radius)) * offset
                    gradient[dx + radius, dy + radius] += strenght
        gradients[i] = gradient
    return gradients


def generate_tilemap(tiles, size, base_height, radius, domain_offset, iterations, gradients, seed):
    tilemaps = {}
    seeds = []
    min_arr = []
    max_arr = []
    for i in range(tiles):
        variable_seed = seed * 2 ** i
        seeds.append(variable_seed)
        # influence = np.full((size, size), 1, dtype=float)
        tilemap = generate_heightmap(size, base_height, radius, domain_offset, iterations, gradients, seeds[i])

        tilemaps[i] = tilemap

        # getting the minimum and maximum of each tile

        min_arr.append(np.min(tilemaps[i]))
        max_arr.append(np.max(tilemaps[i]))

        # getting the minimum and maximum among the three tiles

    tot_min = np.min(min_arr)
    tot_max = np.max(max_arr)

    print(tot_min)
    print(tot_max)
    return tilemaps


def generate_heightmap(size, base_height, radius, domain_offset, iterations, gradients, seed):
    random.seed(seed)
    np.random.seed(seed)

    # initializing the heightmap with a base terrain height
    heightmap = base_height.copy()

    # midpoint of the map
    halfsize = [size // 2, size // 2]

    # i = index of iteration (which iteration it's simulating rn)
    for i in range(iterations):
        for j in range(2 * i):  # more iterations = more points generated  j = number of circles per iteration
            x = random.randint(halfsize[0] - domain_offset, halfsize[0] + domain_offset)
            y = random.randint(halfsize[1] - domain_offset, halfsize[1] + domain_offset)

            gradient = gradients[i]

            # apply gradients
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if (x + dx) % size < size and (y + dy) % size < size:
                        heightmap[(x + dx) % size, (y + dy) % size] += gradient[dx + radius, dy + radius]

            halfsize[0] = x
            halfsize[1] = y
            domain_offset = radius
            radius -= int(1 - (i / iterations))

            # radius = radius - int(1/(i+1))
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    heightmap = (heightmap - min_height) / (max_height - min_height) * 255
    return heightmap


def save_heightmap_as_image(heightmap, filename):
    # Normalize the heightmap to be in the range [0, 255]
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    normalized_heightmap = ((heightmap - min_height) / (max_height - min_height) * 255).astype(np.uint8)
    # Create an image from the normalized heightmap
    image = Image.fromarray(normalized_heightmap.astype(np.uint8), mode='L')
    image.save(filename)


tile_size = 100  # size of the map
base_height = np.full((tile_size, tile_size), 255, dtype=float)  # initial height of the map
radius = 100  # initial radius of the circle around the chosen point (has to be at least half of the tile size) larger values = smaller features = wider view
offset = 100  # how much you want to dig down or bring up (negative numbers have better results
domain_offset = 0  # how close should the next-gen circles be from the first. It is initialized as half the map so the whole map is a candidate for the firs point
iterations = 8  # how many generations to compute (low values make for crisper lines, high values make for more fractal-like appearance
seed = 6739  # seed of the random number generator
tiles = 3

gradients = precompute_gradients(radius, iterations, offset)
tilemap = generate_tilemap(tiles, tile_size, base_height, radius, domain_offset, iterations, gradients, seed)

name = random.randint(0, 100000)
# z = np.array(heightmap)
# x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))
#
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot_surface(x, y, z)
# plt.title('Heightmap')
# plt.show()
#
# plt.imshow(heightmap, cmap='terrain')
# plt.colorbar()
# plt.title('Heightmap')
# plt.show()

fig, axes = plt.subplots(1, len(tilemap), figsize=(12, 6))
for i in range(tiles):
    filename = f'heightmap{name + i}.png'
    save_heightmap_as_image(tilemap[i], filename)
    axes[i].imshow(tilemap[i], cmap='terrain')
    axes[i].set_title('Tile 0')
    axes[i].axis('off')

plt.tight_layout()
fig.subplots_adjust(wspace=0)
plt.show()
