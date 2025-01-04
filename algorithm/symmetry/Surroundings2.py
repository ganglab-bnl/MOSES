import numpy as np
from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Lattice2 import Lattice

class Surroundings2:
    def __init__(self, lattice: Lattice):
        """
        Manager class for creating, transforming, and comparing VoxelSurroundings 
        matrices for a given lattice design.
        """
        self.lattice = lattice

    def voxel_surroundings(self, voxel) -> dict[tuple[float, float, float], int]:
        """
        Get the VoxelSurroundings for a given voxel in the UnitCell, in which each value 
        represents the voxel.material for each voxel and its VoxelSurroundings.
        
        Args:
            voxel: The Voxel object to build VoxelSurroundings around
        Returns:
            voxel_surroundings: 3D numpy array of tuples (voxel.material, voxel.index) 
        """
        voxel = self.lattice.get_voxel(voxel) if isinstance(voxel, int) else voxel

        z_len, y_len, x_len = self.lattice.MinDesign.shape
        max_len = max(z_len, y_len, x_len)

        # create a surroundings cube at least max_len out from the center
        coord_range = np.linspace(-max_len, max_len, 2*max_len+1)
        x, y, z = np.meshgrid(coord_range, coord_range, coord_range, indexing='ij')
        coords = np.array([x.flatten(), y.flatten(), z.flatten()]).T

        surr = {}
        for coord in coords:
            # convert voxel_surr coords into an index into the original lattice
            x, y, z = coord + np.array(voxel.coordinates)
            og_x = int((x_len + x) % x_len)
            og_y = int((y_len + y) % y_len)
            og_z = int((z_len + z) % z_len)
            
            og_voxel = self.lattice.voxels[(og_x, og_y, og_z)]
            og_mat = og_voxel.material

            surr[tuple(coord)] = og_mat

        return surr
    

    def rotate(self, surr_dict: dict[tuple[float, float, float], int], rotation) -> dict[tuple[float, float, float], int]:
        """
        Accepts a surroundings dictionary (coords: mat) and rotates each coordinate 
        based on the supplied rotation function.

        Args:
            surr_dict
            rotation

        Returns:
            rot_surr
        """
        # convert coords and materials to their own np.arrays
        surr_keys = np.array(list(surr_dict.keys()))
        surr_values = list(surr_dict.values())

        # apply rotation
        rot_surr_keys = rotation(surr_keys)
        rot_surr_keys = np.round(rot_surr_keys).astype(int)
        rot_surr = {tuple(key): value for key, value in zip(rot_surr_keys, surr_values)}

        return rot_surr