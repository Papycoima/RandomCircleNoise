
# algorithm that generates terrain-like heightmaps
# imagined by me, Daniele Chirico, July 15, 2024

import numpy as np
import random
import matplotlib.pyplot as plt
from PIL import Image

#-----Process-----#
# start with a flat heightmap filled with a base terrain height
# select a random point in that heightmap
# take a random offset value, positive or negative
# create a circle with a large enough radius that creates a hole or a bulge as tall as the offset
# select points near the edge of the circe (points that belong to the "domain")
# repeat process

#-----Details-----#
# radii should get smaller with each iteration (or not, depending on which one creates a better result)
# number of circles should get larger with each iteration
# offset should get smaller with each iteration
# holes and bulges should have a gradient, not have a sharp edge

#-----Requirements-----#
# has to be perfectly tilable
# has to be somewhat fast (for the time being is not very fast - the slowest process is the gradient calculator)
# has to rely on some seed (same seed = same heightmap)


def generate_heightmap(size, base_height, radius, offset, domain_offset, iterations, seed):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    # initializing the heightmap with a base terrain height
    i = 0
    heightmap = base_height
    # midpoint of the map
    halfsize = [int(size / 2), int(size / 2)]
    
    while i < iterations:

        flip = random.choice((-1, 1)) # to choose if the offset will dig down or bring up the terrain
        offset = offset * flip

        j = 0
        while j <= i: # more iterations = more points generated
            x = random.randint(halfsize[0] - domain_offset, halfsize[0] + domain_offset)
            y = random.randint(halfsize[1] - domain_offset, halfsize[1] + domain_offset)

        #-----gradient-----#
            for dx in range(-int(radius), int(radius)):
                for dy in range(-int(radius), int(radius)):
                    distance = np.sqrt((dx ** 2) + (dy ** 2))
                    if distance <= radius:
                        strenght = (1 - (distance/radius)) * offset
                        heightmap[(x+dx) % size, (y + dy) % size] += strenght


            min = np.min(heightmap)
            max = np.max(heightmap)
            halfsize[0] = x
            halfsize[1] = y
            domain_offset = radius
            radius = radius - int(i / iterations)

            j += 1
        i += 1

    for a in range(0, size):
        for b in range(0, size):
            heightmap[a, b] = normalize(heightmap[a, b], min, max)

    return heightmap


def save_heightmap_as_image(heightmap, filename):
    # Normalize the heightmap to be in the range [0, 255]
    min_height = np.min(heightmap)
    max_height = np.max(heightmap)
    normalized_heightmap = ((heightmap - min_height) / (max_height - min_height) * 255).astype(np.uint8)

    # Create an image from the normalized heightmap
    image = Image.fromarray(normalized_heightmap, mode='L')
    image.save(filename)

def normalize(value, min, max):
    normalized = 256 * (value - min) / (max - min)
    return normalized

size = 100 # size of the map
base_height = np.full((size,size), 0, dtype=float) # initial height of the map
radius = 100 # initial radius of the circle around the chosen point (has to be at least half of the tile size)
offset = -100 # how much you want to dig down or bring up (negative numbers have better results
domain_offset = 0 # how close should the next-gen circles be from the first. It is initialized as half the map so the whole map is a candidate for the firs point
iterations = 10 # how many generations to compute
seed = 67458 # seed of the random number generator

heightmap = generate_heightmap(size, base_height, radius, offset, domain_offset, iterations, seed)

name = random.randint(0, 10000000)

filename = f'heightmap{name}.png'
save_heightmap_as_image(heightmap, filename)

z = np.array(heightmap)
x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z)
plt.title('Heightmap')
plt.show()

plt.imshow(heightmap, cmap='terrain')
plt.colorbar()
plt.title('Heightmap')
plt.show()
