# Random Circle Noise
An algorithm that generates terrain-like heightmaps. Designed by Daniele Chirico on July 15, 2024.

## How it works

### The algorithm
The process is pretty simple: start with a blank tile. Select random points and trace a circle around each one of them. Now select other random points and trace a smaller circle around each one of them. Repeat until the tile has sufficent details.
The algorithm itself does not produce infinite procedural terrain, but a single tile can perfectly tile itself. I exploited this feature to create an island by copying the tile nine times in a 3x3 grid and simply applying a fading gradient all around to create the ocean.
The algorithm relies on a seed, so the same seed will produce the same heightmap. Results also vary if the size of the tile or the radius of the circles are changed.

### Controls
"tile_size" controls the sidelength of a single tile.
"radius" controls the initial radius of the circles that generate the heightmap. The radius gets smaller with each iteration. The number of iteration is dictated by how many times the radius can be downscaled before getting to zero. So a larger radius means more iterations, and more iterations mean higher level of detail. The processing time depends mostly on the size of the radius.
"seed", as already said, is the seed of the algorithm. It is used to set up the "random" module, which will then randomly choose all the points on the tile.

### Output
The program outputs .PNGs of both each individual tile, named "heightmap" followed by random numbers, and the whole 3x3 grid heightmap, named "heightmap"-random numbers-"final".
