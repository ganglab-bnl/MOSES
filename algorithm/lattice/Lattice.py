
import numpy as np
from algorithm.lattice.Voxel import Voxel, Bond

class Lattice:
    """store the basic unit cell"""
    def __init__(self, voxels: list[Voxel], is_unit_cell: bool=True):
        
        # get the dimensions of the lattice that was inputted
        x = 0 if is_unit_cell else 1
        self.xdim = max([v.coords[0] for v in voxels]) +x
        self.ydim = max([v.coords[1] for v in voxels]) +x
        self.zdim = max([v.coords[2] for v in voxels]) +x
        self.dimensions = self.xdim, self.ydim, self.zdim
        self.unit_dimensions = [d+x for d in self.dimensions]

        # print(f"lattice found dimensions: {self.xdim, self.ydim, self.zdim}")

        self.voxels = voxels
        self.unit_cell_voxels = []
        self.voxel_dict = {}
        self.init_voxels(voxels, is_unit_cell)
        self.fill_partners()

    def init_voxels(self, voxels: list[Voxel], is_unit_cell: bool=True):
        """fills in self.voxels and self.unit_cell_voxels based on whether
        the user supplied a unit cell or not"""

        # set initial voxel.id's (prob a more elegant soln, find later)
        for i, v in enumerate(self.voxels):
            v.id = i

        # --- IS A UNIT CELL ---
        if is_unit_cell:
            for v in self.voxels:
                # if in the last layer of any dimension
                if v.coords[0]==self.xdim or v.coords[1]==self.ydim or v.coords[2]==self.zdim:
                    print(f"v{v.id} in last layer {v.coords}")
                    self.unit_cell_voxels.append(v)
            
            for v in self.unit_cell_voxels:
                self.voxels.remove(v)
                
            # redo the id's
            for i, v in enumerate(self.voxels):
                v.id = i
            for i, v in enumerate(self.unit_cell_voxels):
                v.id = i + len(self.voxels)
            
            # redo the IDs
            for v in self.voxels:
                self.voxel_dict[v.coords] = v.id
            
        # --- IS NOT A UNIT CELL ---
        # parse voxels for unit_cell_voxels and voxels
        elif not is_unit_cell:
            # redo the IDs
            for v in self.voxels:
                self.voxel_dict[v.coords] = v.id

            xy_layer = [(x, y, self.unit_dimensions[2]-1) for x in range(self.unit_dimensions[0]) for y in range(self.unit_dimensions[1])]
            yz_layer = [(self.unit_dimensions[0]-1, y, z) for y in range(self.unit_dimensions[1]) for z in range(self.unit_dimensions[2])]
            xz_layer = [(x, self.unit_dimensions[1]-1, z) for x in range(self.unit_dimensions[0]) for z in range(self.unit_dimensions[2])]

            all_old_coords = []
            for new_coords in xy_layer:
                old_coords = (new_coords[0] % (self.dimensions[0]), new_coords[1] % (self.dimensions[1]), 0)
                all_old_coords.append(old_coords)
            for new_coords in yz_layer:
                old_coords = (0, new_coords[1] % (self.dimensions[1]), new_coords[2] % (self.dimensions[2]))
                all_old_coords.append(old_coords)
            for new_coords in xz_layer:
                old_coords = (new_coords[0] % (self.dimensions[0]), 0, new_coords[2] % (self.dimensions[2]))
                all_old_coords.append(old_coords)

            # iterate through the unit layers and add the corresponding voxels
            seen = set()
            for i, new_coords in enumerate(xy_layer + yz_layer + xz_layer):
                if new_coords in seen: # ignore overlapping coordinates
                    continue
                # create new voxel which would correspond to here
                old_coords = all_old_coords[i]
                old_v = self.get_voxel(old_coords)
                new_v = Voxel(
                    coords=new_coords,
                    cargo=old_v.cargo,
                    cargo_coords=old_v.cargo_coords,
                    id=len(voxels) + len(self.unit_cell_voxels)
                )
                self.unit_cell_voxels.append(new_v)
                seen.add(new_coords)
                # print(f'adding new voxel @ {new_coords}')


    def find_partner(self, voxel, vertex: tuple[float,float,float]) -> tuple[Voxel, Bond]:
        """given a voxel and a vertex on that voxel, return what voxel in the lattice it's connected to
        
        Args:
            voxel: Voxel or voxel.id corresponding to what you want to find partner of
            vertex: coordinate of the vertex wrt. voxel
        Returns:
            partner_voxel, partner_bond
        """
        v = self.get_voxel(voxel)
        partner_coords = tuple(np.array(v.coords) + 2*np.array(vertex))

        # wrap around to make sure it's within our coordinate bounds
        px, py, pz = partner_coords[0] % self.xdim, partner_coords[1] % self.ydim, partner_coords[2] % self.zdim
        pv = self.get_voxel((px,py,pz))

        # also get partner bond in that direction
        pb_vertex = tuple(-np.array(vertex)) # convert direction to vertex (1/2)
        pb = pv.get_bond(pb_vertex)

        return pv, pb
    
    def fill_partners(self):
        """fill in all bond partners in voxel objects in place"""
        for v in self.voxels:
            for vertex in v.vertices:
                b = v.get_bond(vertex)
                # skip if bond already has partner
                if b.partner is not None:
                    continue
                pv, pb = self.find_partner(v, vertex)
                # set the partners
                b.set_partner(pb)
                pb.set_partner(b)

    def get_voxel(self, v) -> Voxel:
        """ get the voxel obj in the lattice based on either its ID or its lattice coords """
        if isinstance(v, Voxel): # CASE 0: supplied Voxel object already
            return v
        elif isinstance(v, int): # CASE 1: supplied voxel.id (int)
            voxel_obj = self.voxels[v]
        elif isinstance(v, tuple): # CASE 2: supplied lattice coords (tuple)
            i = self.voxel_dict[v]
            voxel_obj = self.voxels[i]
        elif isinstance(v, np.ndarray): # CASE 3: supplied lattice coords (np)
            i = self.voxel_dict[tuple(v)]
            voxel_obj = self.voxels[i]
        else: # CASE 4: invalid type
            raise ValueError(f"invalid voxel.id type: {type(v)}")
        
        return voxel_obj