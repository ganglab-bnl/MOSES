from math import ceil, floor
import numpy as np
from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Lattice import Lattice


class Surroundings:
    def __init__(self, lattice: Lattice):
        """
        Manager class for creating, transforming, and comparing VoxelSurroundings 
        matrices for a given lattice design.
        """
        self.FullSurroundings = self._init_full_surroundings(lattice)

    def voxel_surroundings(self, voxel: Voxel, verbose=False):
        """
        Get the VoxelSurroundings for a given voxel in the UnitCell, in which each value 
        represents the voxel.material for each voxel and its VoxelSurroundings.
        @param:
            - voxel: The Voxel object to build VoxelSurroundings around
        @return:
            - VoxelSurroundings: 3D numpy array of tuples (voxel.material, voxel.index) 
        """

        # How far down to go in each direction
        og_zlen, og_ylen, og_xlen = self.MinDesign_dimensions # original dimensions of MinDesign
        z_repeats, y_repeats, x_repeats = self.tile_repeats # how many times MinDesign is repeated in xyz directions in FullSurroundings

        # Get halfway points for each direction
        # (x_0, y_0, z_0) corresponds to the (0,0,0) position of the middle MinDesign
        z_0 = floor(z_repeats / 2) * og_zlen
        y_0 = floor(y_repeats / 2) * og_ylen
        x_0 = floor(x_repeats / 2) * og_xlen

        # Get voxel's new coordinates within middle MinDesign
        vox_z = z_0 + voxel.np_index[0]
        vox_y = y_0 + voxel.np_index[1]
        vox_x = x_0 + voxel.np_index[2]

        max_og_len = max(og_zlen, og_ylen, og_xlen)
        extend_amt = floor(max_og_len / 2)

        if verbose:
            print(f"Halfway points for each direction: ({z_0, y_0, x_0})")
            print(f"Slicing full_surr @ ({vox_z, vox_y, vox_x})")

        VoxelSurroundings = self.FullSurroundings[(vox_z-extend_amt) : (vox_z+extend_amt+1),
                                                 (vox_y-extend_amt) : (vox_y+extend_amt+1),
                                                 (vox_x-extend_amt) : (vox_x+extend_amt+1)]

        return VoxelSurroundings

    def _init_full_surroundings(self, lattice: Lattice):
        """
        Initialize a FullSurroundings from all voxels in Lattice.MinDesign,
        which all other SurroundingsMatrices will be subset from.
        @param:
            - lattice: A Lattice object
        @return:
            - full_surroundings: 3D numpy array of ints
        """
        max_len = max(np.shape(lattice.MinDesign))
        final_len = 3 * max_len

        # Get dimensions of MinDesign (we are tiling MinDesign)
        z_len, y_len, x_len = lattice.MinDesign.shape
        self.MinDesign_dimensions = [z_len, y_len, x_len]

        # I imagine z=layers, y=rows, x=columns
        z_repeats = ceil(final_len / z_len)
        y_repeats = ceil(final_len / y_len) 
        x_repeats = ceil(final_len / x_len) 

        # If x, y, or z repeats are even, add 1 to make them odd
        # (ensures the original voxel is in the center of FullSurroundings)
        if z_repeats % 2 == 0:
            z_repeats += 1
        if y_repeats % 2 == 0:
            y_repeats += 1
        if x_repeats % 2 == 0:
            x_repeats += 1

        # Tile the surroundings matrix [dim]repeats times in each direction
        self.tile_repeats = [z_repeats, y_repeats, x_repeats]
        full_surroundings = np.tile(lattice.MinDesign, self.tile_repeats)

        return full_surroundings