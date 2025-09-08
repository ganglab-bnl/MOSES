import numpy as np
from algorithm.lattice.Lattice import Lattice

class Surroundings:
    def __init__(self, lattice: Lattice):
        self.lattice = lattice


    def voxel_surroundings(self, voxel) -> dict[tuple[float, float, float], int]:
        """
        create a cube of surrounding particles all oriented wrt. where 
        v.cargo_coords would be
        """
        v = self.lattice.get_voxel(voxel)

        xdim, ydim, zdim = self.lattice.dimensions
        max_dim = max(xdim, ydim, zdim)

        # create a surroundings cube at least max_len out from the center
        coord_range = np.linspace(-max_dim, max_dim, 2*max_dim+1)
        x, y, z = np.meshgrid(coord_range, coord_range, coord_range, indexing='ij')
        coords = np.array([x.flatten(), y.flatten(), z.flatten()]).T

        surr = {}
        for coord in coords:
            # convert voxel_surr coords into an index into the original lattice
            x, y, z = coord + np.array(v.coords)
            og_x = int((xdim + x) % xdim)
            og_y = int((ydim + y) % ydim)
            og_z = int((zdim + z) % zdim)
            
            og_voxel = self.lattice.get_voxel((og_x, og_y, og_z))

            # translate the coordinate a little for the accurate surroundings
            coord = coord + np.array(og_voxel.cargo_coords)
            surr[tuple(coord)] = og_voxel.cargo

        return surr
    

    def rotate(self, surr_dict: dict[tuple[float, float, float], int], rotation) -> dict[tuple[float, float, float], int]:
        """
        accepts a surroundings dictionary (coords: cargo) and rotates each coordinate 
        based on the supplied rotation function
        """
        # convert coords and materials to their own np.arrays
        surr_keys = np.array(list(surr_dict.keys()))
        surr_values = list(surr_dict.values())

        # apply rotation
        rot_surr_keys = rotation(surr_keys)
        rot_surr_keys = np.round(rot_surr_keys, 2)
        rot_surr = {tuple(key): value for key, value in zip(rot_surr_keys, surr_values)}

        return rot_surr

if __name__ == "__main__":
    from algorithm.lattice.Voxel import Voxel

    # a sample oriented lattice
    # --- layer 0 ---
    v0 = Voxel(coords=(0,0,0), cargo=1, cargo_coords=(0,0,0))
    v1 = Voxel(coords=(1,0,0), cargo=1, cargo_coords=(0,0,-0.5))
    v2 = Voxel(coords=(0,1,0), cargo=1, cargo_coords=(0,0,-0.5))
    v3 = Voxel(coords=(1,1,0), cargo=1, cargo_coords=(0,0,0))

    # --- layer 1 ---
    v4 = Voxel(coords=(0,0,1), cargo=2, cargo_coords=(0,0,0.5))
    v5 = Voxel(coords=(1,0,1), cargo=2, cargo_coords=(0,0,0))
    v6 = Voxel(coords=(0,1,1), cargo=2, cargo_coords=(0,0,0))
    v7 = Voxel(coords=(1,1,1), cargo=2, cargo_coords=(0,0,0.5))

    voxels = [v0, v1, v2, v3, v4, v5, v6, v7]

    # test creating lattice from unit cell and not from unit cell ✅
    lattice = Lattice(voxels, is_unit_cell=False)
        
    surr = Surroundings(lattice)
    v0_surr = surr.voxel_surroundings(0)

    print(v0_surr)