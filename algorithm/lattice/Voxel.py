import logging

class Bond:
    def __init__(self, voxel: 'Voxel'=None, vertex: tuple[float, float, float]=None, 
                 color: int=None, type: str=None, partner: 'Bond'=None):
        self.voxel = voxel
        self.vertex = vertex
        self.color = color
        self.type = type
        self.partner = partner

    # setting methods
    def set_color(self, color: int):
        self.color = color
    def set_partner(self, partner: 'Bond'):
        self.partner = partner
    def set_type(self, type: str=None):
        self.type = type

    # getting methods
    def get_partner(self) -> 'Bond':
        return self.partner
    def get_label(self) -> str:
        i = self.voxel.vertices.index(self.vertex)
        return self.voxel.v_names[i]
    def get_partner_voxel(self) -> 'Voxel|None':
        return self.partner.voxel if self.partner else None

class Voxel:
    def __init__(self, coords: tuple[float, float, float], cargo: int, 
                 cargo_coords: tuple[float, float, float], id: int=None):
        """the essential unit of our lattice ---
        a point group with 6 bonds + an oriented cargo"""

        # essential info
        self.id = id # ID is the voxel's index into parent Lattice)
        self.coords = coords
        self.cargo = cargo
        self.cargo_coords = cargo_coords
        # mesovoxel id - which unique voxel in the unique set does this correspond 
        # to, and is it complementary? (-)
        self.id2 = None

        # vector (euclidean) representing direction of each vertex 
        # wrt. the voxel @ (0,0,0)
        self.vertices = [
            (0.5, 0, 0), (-0.5, 0, 0),   # +-x
            (0, 0.5, 0), (0, -0.5, 0),   # +-y
            (0, 0, 0.5), (0, 0, -0.5)    # +-z
        ]
        self.v_names = [ # for labeling purposes
            "+x", "-x", 
            "+y", "-y", 
            "+z", "-z"
        ]

        # initialize bonds
        self.bonds: dict[tuple[float, float, float], Bond] = {}
        for v in self.vertices:
            self.bonds[v] = Bond(voxel=self, vertex=v)

    def get_bond(self, vertex: tuple[float, float, float]) -> Bond|None:
        return self.bonds.get(vertex, None)
    
    def get_partner(self, vertex: tuple[float, float, float]) -> tuple['Voxel', Bond]:
        """
        get the partner Voxel + Bond objects in the supplied vertex
        """
        bond = self.get_bond(vertex)
        pv = bond.get_partner_voxel()
        pb = bond.get_partner()
        if pv is None or pb is None:
            logging.error(f"No bond partner found for Voxel {self.id} in direction {vertex}")
            return None, None
        return pv, pb
    
    def set_id2(self, id2: int):
        """sets the unique mesovoxel id of the voxel
        where (+) is structural, (-) is complementary"""
        self.id2 = id2

    def is_touching(self, voxel_id: int, type: int=1):
        """returns whether the given voxel_id (type==1 or 2) is touching the current voxel"""
        for _, bond in self.bonds.items():
            if bond.partner.voxel.id==voxel_id and type==1:
                return True
            elif bond.partner.voxel.id2==voxel_id and type==2:
                return True
        return False

    def __str__(self):
        str1 = f"voxel (id1={self.id}, id2={self.id2}) @ {self.coords} | cargo={self.cargo} @ {self.cargo_coords}:\n---"
        for v_coords, bond in self.bonds.items():
            i = self.vertices.index(v_coords)
            str2 = f"\n -> {self.v_names[i]}: color={bond.color}, type={bond.type}"
            str1 = str1+str2

        return str1