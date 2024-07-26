
import numpy as np
import random
import matplotlib.pyplot as plt
import math
from PIL import Image


def precompute_gradients(size):
    gradients = []
    for i in range(0, 9):
        gradient = np.full((size, size), 0, dtype=float)
        for x in range(size):
            for y in range(size):
                if i == 0:
                    distance = math.sqrt(((x - size) ** 2) + ((y - size) ** 2))
                    if distance <= size:
                        strenght = (1 - (distance / size))
                        gradient[x, y] = strenght
                if i == 1:
                    value = x / size
                    gradient[x, y] = value
                if i == 2:
                    distance = math.sqrt(((x - size) ** 2) + (y ** 2))
                    if distance <= size:
                        strenght = (1 - (distance / size))
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
                    distance = math.sqrt((x ** 2) + ((y - size) ** 2))
                    if distance <= size:
                        strenght = (1 - (distance / size))
                        gradient[x, y] = strenght
                if i == 7:
                    value = (size - x) / size
                    gradient[x, y] = value
                if i == 8:
                    distance = math.sqrt((x ** 2) + (y ** 2))
                    if distance <= size:
                        strenght = (1 - (distance / size))
                        gradient[x, y] = strenght
        gradients.append(gradient)
    return gradients


def precompute_circles(r, offset, iterations):
    circles = {}
    for i in range(iterations):
        offset *= 1 / (i + 1)
        r *= (((-i) / 7) + 1)
        r = int(r)
        if r > 0:
            circle = np.full((2 * r + 1, 2 * r + 1), 0, dtype=float)
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    distance = np.sqrt((dx ** 2) + (dy ** 2))
                    if distance <= r:
                        strenght = (1 - (distance/r)) * offset
                        circle[dx + r, dy + r] += strenght
            circles[i] = circle
        elif r <= 0:
            break
    return circles


def generate_tilemap(size, circles):
    tilemaps = {}
    gradients = precompute_gradients(tile_size)
    main_tile = generate_heightmap(size, circles)
    for i in range(0, 9):
        tilemap = main_tile * gradients[i]
        tilemaps[i] = tilemap
    return tilemaps


def generate_heightmap(size, gradients):
    # initializing the heightmap with a base terrain height
    heightmap = np.full((size, size), 128, dtype=float)

    # midpoint of the map
    halfsize = [size // 2, size // 2]
    iterations = len(gradients)

    # i = index of iteration (which iteration it's simulating at the moment)
    for i in range(iterations):
        for j in range(20 * i):  # more iterations = more points generated  j = number of circles per iteration

            x = random.randint(0, size)
            y = random.randint(0, size)

            gradient = gradients[i]
            r = int(((len(gradient) - 1) / 2))
            print(int(((len(gradient) - 1) / 2)))

            # apply gradients
            for dx in range(-r, r + 1):
                for dy in range(-r, r + 1):
                    heightmap[(x + dx) % size, (y + dy) % size] += gradient[dx + r, dy + r]

            halfsize[0] = x
            halfsize[1] = y

    heightmap = -heightmap
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    if min_height < 0 or max_height > 255:
        heightmap = (heightmap - min_height) / (max_height - min_height) * 255
    return heightmap


def join_tiles(tile_arr):
    sidelength = len(tile_arr)
    resolution = len(tile_arr[0])
    final_heightmap = np.full((resolution * 3, resolution * 3), 0, dtype=float)
    for i in range(sidelength // 3):
        for y in range(resolution):
            for j in range(sidelength // 3):
                tile = tile_arr[(3 * i) + j]
                for x in range(resolution):
                    value = tile[y, x]
                    final_heightmap[y + (resolution * i), x + (resolution * j)] = value
    return final_heightmap


def save_heightmap_as_image(heightmap, filename):
    # Create an image from the heightmap
    image = Image.fromarray(heightmap.astype(np.uint8), mode='L')
    image.save(filename)


tile_size = 128  # size of the tile.
radius = 256  # initial radius of the circle around the chosen point. larger values = smaller features.
seed = 8675746  # seed of the random number generator.

# 36472423 isola del Napoli
# 8675746 seed fico size = 128, radius = 256
# 456894576 size = 128, radius = 256
# 4718462


random.seed(seed)
name = random.randint(0, 100000)

circles = precompute_circles(r=radius, offset=100, iterations=10)
tilemap = generate_tilemap(size=tile_size, circles=circles)
final_tilemap = join_tiles(tilemap)

save_heightmap_as_image(final_tilemap, f'heightmap{name} final.png')


plt.imshow(final_tilemap, cmap='terrain')
plt.colorbar()
plt.title('Heightmap')
plt.show()
