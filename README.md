# MOSES

This repository provides the official implementation of the **MOSES algorithm** from the following paper.

The problem statement is: given a lattice design with particles in certain positions, how can we color the edges to enable the DNA origami to _self assemble_ into the desired design?

We propose a kind of symmetry-informed edge coloring algorithm which utilizes the symmetries of each DNA origami building block - an octahedron connected at the 6 vertices (+- x, y, z). Our algorithm is trying to decide what unique DNA sequences, or 'colors' we should prescribe to each vertex in order to enable this self assembly. The goal is to minimize the number of unique origami-bond combinations, which improves the structural integrity of the final experimental lattice result.

## Installation

Download the repository, then install the requirements in your preferred location (venv, conda, etc.) with the following:
```shell
pip install -r requirements.txt
```
Note that you may need to install Qt onto your system in order to run some of the visualizations / applications. If you need help installing any requirements or if something breaks, please contact Sarah Hong (ssh2198@columbia.edu) for troubleshooting.

## Setup 1: The data structures 
The following data structures in `/algorithm/lattice/` help us create the Lattice structure in preparation for the coloring algorithm.

<img width="244" alt="Picture1" src="https://github.com/user-attachments/assets/7ccfb863-5590-4cff-8ed3-72da8e840191">

### The Voxel
`Voxel` - The basic building block of the system - currently represents an octahedral DNA origami with 6 vertices (+- x, y, z) which can contain a material cargo centered inside.

### The Bond
`Bond` - A high level representation of the DNA sequence which connects different Voxels together. Different sequences are abstracted with "colors" - our algorithm doesn't care about assigning the specifics of what colors go where, we only care that certain vertices have the same sequence or don't.

### The Lattice
`Lattice` - Contains the final arrangement of Voxels and Bonds which the user can design and visualize. It is assumed to tile out infinitely in space according to the defined unit cell structure which the user provides.

## Setup 2: Symmetry computations
The following setup modules are found in `algorithm/symmetry/` and help define the concept of a "symmetry" operation and a "relation", which respectively inform the ways in which two voxels can be structurally equivalent or bond-level equivalent to each other.

### Symmetries
We define a **symmetry operation** between two voxels to be as follows:
- Take the `Voxel` and its `VoxelSurroundings` (the lattice tiled out around it in a large-enough cube), transform it with some rotation (say, 90° X-axis), and overlay it on top of another voxel. If each particle in the surroundings overlays on top of each other 1-to-1, then the two voxels satisfy 90° X-axis symmetry with each other.

<img width="1000" alt="surroundings" src="https://github.com/user-attachments/assets/391ede6c-3ae2-419e-b481-3ccdbf50980b">

We compute all possible symmetry operations between all combinations of Voxels in the Lattice and then store it in a dataframe, `SymmetryDf`. 

Most notably, this helper function of SymmetryDf will be useful in the painting stage.
- `SymmetryDf.symlist(voxel_1, voxel_2)` - Return a list of all valid symmetries between two voxels

## Painting algorithm
### Background / Data Structures
The goal behind our painting algorithm is to create a coloring scheme for the lattice. There exists the trivial solution to paint each vertex a different color, but this is entropically very unfavorable to form in real life. Thus the goal is to minimize the total number of unique origami and number of colors to be able to reuse voxels as much as possible.

We define the **Mesovoxel**, which is the set of all unique voxels in the lattice. The Mesovoxel contains two sets:
1. Structural voxels
2. Complementary voxels

With the property that each structural voxel has one associated complementary voxel which it may bind to.

The idea behind the algorithm is to start out with a set of structurally unique voxels (which we know using voxel symmetries alone) and then iteratively adding more complementary voxels as we need, until the entire lattice is painted.

We have the following **binding constraints** which limit how we can color the bonds:
1. Color complementarity: All colors(+) must be binded to its complement(-)
2. No palindromes: A color(+) and its complement(-) cannot exist on the same voxel

There is another consideration, which is that each painting operation affects not only the given voxel but also its neighbor. Thus we introduce the set of _"painted_voxels"_, which we update each time we paint a pair of vertices. 

### The Algorithm
On a high level, the current coloring algorithm is as follows:

**Phase 1:** Painting structural bonds
1. Define all structurally unique voxels using SymmetryDf
2. Paint all bonds between structural voxels, update `painted_voxels` with new set of voxels
3. Paint self-symmetries on all voxels in painted_voxels, iteratively updating `painted_voxels` until no change.

**Phase 2:** Painting complementary bonds
1. Paint a new complementary bond (and its partner) on an unpainted vertex in the lattice.
2. Paint both voxels with their self symmetries, updating painted_voxels. Keep painting self symmetries for all voxels in `painted_voxels` until no change.
3. For all new voxels we painted which are not yet in the Mesovoxel, find the best "mesoparent" in the Mesovoxel. (Eg, what voxel do we already have in the Mesovoxel which looks like it?)

Split branch after 3:

1. If the only valid mesoparent has "negation" Voxel relation (complementary bonds have opposite complementarity), then we consider this voxel that voxel's "complement" and add it to the Mesovoxel.
2. If there exists a valid mesoparent with "equal" Voxel relation, then we add this new voxel to that mesoparent's `maplist[]` and update all other voxels which are mapped to it with the new information.

### Post-processing: Binding Flexibility
Finally as a post-processing routine, we give users an optional "binding flexibility" parameter, which modifies the final painting result to be stricter or looser. This is motivated by the observation that the geometry / symmetries of specific structures may perform better under different constraints, and we offer the user the option to make it more/less strict.

**Binding flexibility 1:** Reduces specificity (less colors)
- BF 1 turns all bonds to voxels in the same automorphism equivalence class are repainted to be the same color. 
- In other words, we repaint all bonds between all voxels with some symmetry between them to be the same color.

**Binding flexibility 2:** No change
- BF 2 is the default result from the `Painter.paint()` algorithm. It generally leads to the best results, so most systems are painted with this.

**Binding flexibility 3:** Adds specificity (more colors)
- Introducing a maximum cutoff ratio (= structural bonds / total bonds) per voxel.
- For all voxels in the lattice with a cutoff ratio higher than the maximum, we repaint a NEW color ontop of a structural bond on that voxel to lower the ratio to satisfy the constraint.
- This ratio is motivated by the observation that having more structural bonds on the same voxel makes it more likely to erroneously bind in ways we don't want.

## GUI application

To test out a simple GUI to create and visualize lattices, you can either run the scripts in a Jupyter notebook (see `notebooks/algorithm.ipynb` for detailed usage) or by running a standalone application to test multiple at once.

The application can be run with the command:

```shell
python main.py
```

And the application features two main modes.

### 1. Design
Create a lattice with your desired dimensions and click "Save lattice" when done, then move to the "Visualize" tab to see the colored lattice.

<img width="550" alt="Screenshot 2024-11-10 at 1 51 51 AM" src="https://github.com/user-attachments/assets/a00467a0-51c4-45ca-81c6-49128204c32e">

### 2. Visualize
Runs the algorithm and visualizes the colored bonds.

<img width="550" alt="Screenshot 2024-11-10 at 1 49 31 AM" src="https://github.com/user-attachments/assets/50101e62-32a0-4f6d-9037-3ae8b47408e6">

#### View controls:
- Left button drag / Arrow keys: Rotates the scene around a central point
- Middle button drag: Pan the scene by moving the central “look-at” point within the x-y plane
- Middle button drag + CTRL: Pan the scene by moving the central “look-at” point along the z axis
- Wheel spin: zoom in/out
- Wheel + CTRL(or CMD): change field-of-view angle
