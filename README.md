# MOSES
**MOSES:** Mapping Of Structurally Encoded aSsemblies.

This repository stores the official code from [the following paper](https://pubs.acs.org/doi/10.1021/acsnano.4c17408), _"Arbitrary Design of DNA-Programmable 3D Crystals through Symmetry Mapping."_

The idea behind MOSES is to use the symmetries of the DNA origami lattice to reduce the number of unique voxels needed to create it.
The algorithm is essentially one of information compression, of trying to solve a graph edge-coloring problem given certain assembly constraints.

## Usage
See the `notebooks/orientation.ipynb` walks through the process in creating a lattice, running the MOSES algorithm, and visualizing the painted bonds.

### Example Output
An example of the final visualization can be seen here.

<img width="600" alt="lattice" src="https://github.com/user-attachments/assets/409560be-9215-47b0-9d5f-23515ccd6d35" />

### Contact
If you encounter any errors or need help using the algorithm, please contact ssh2198@columbia.edu.
