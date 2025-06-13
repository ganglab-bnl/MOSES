
from algorithm.lattice.Lattice import Lattice
from algorithm.lattice.Voxel import Bond
from algorithm.symmetry.Surroundings import Surroundings
from algorithm.symmetry.SymmetryDf import SymmetryDf

from algorithm.painting.Mesovoxel import Mesovoxel
from algorithm.painting.Painter import Painter

class Moses:
    """the class for painting via the MOSES algorithm"""
    def __init__(self, lattice: Lattice):
        self.lattice = lattice
        # computes all symmetries, filling symmetry_df
        # with all possible voxel pairs and their symmetries
        self.surroundings = Surroundings(self.lattice)
        self.symmetry_df = SymmetryDf(self.lattice, self.surroundings)  # => a useful function
        self.has_symmetry = lambda v1, v2: self.symmetry_df.has_symmetry(v1, v2)

        # initialize the structural voxels
        self.mesovoxel = Mesovoxel(self.lattice, self.has_symmetry)
        self.painter = Painter(lattice, self.symmetry_df)
        self.n_colors = 0
        self.uncolored_bonds = self.get_uncolored_bonds()
        self.seen_bonds = set(self.uncolored_bonds)

    def str_paint(self):
        """paint an initial path of bonds connecting all structural voxels"""
        for voxel1 in self.mesovoxel.structural_voxels:
            voxel1 = self.lattice.get_voxel(voxel1)

            # --- paint path of structural bonds ---
            for vertex, bond1 in voxel1.bonds.items():
                voxel2, bond2 = voxel1.get_partner(vertex)
                # ensure (1) neither bond is colored yet
                # and (2) the other voxel is in the mesovoxel + structural
                if (bond1.color or bond2.color) or (voxel2.id not in self.mesovoxel.structural_voxels):
                    continue
                # paint the new bond
                # print(f"\n--- PAINT S_BOND ({self.n_colors+1}) --- \nvoxel_{voxel1.id} ({bond1.vertex}) <---> voxel_{voxel2.id} ({bond2.vertex})")
                _ = self.paint_new_bond(bond1, bond2, "structural")

    def comp_paint(self):
        """
        paint all the complementary bonds, slowly adding in complementary 
        voxels (new sub-equivalence class) as needed.
        """
        i = 0
        while i < len(self.uncolored_bonds):

            # get bond / voxel iteration variables
            bond1 = self.uncolored_bonds[i]
            # voxel1 = self.lattice.get_voxel(bond1.voxel)

            i += 1 # early increment for continue safety
            if bond1.color is not None: 
                continue # skip bonds which are already painted

            # get the partner
            voxel2, bond2 = bond1.partner.voxel, bond1.partner

            # CASE 1: VOXEL IS ALREADY MAPPED
            if voxel2.id2: 
                pv = self.mesovoxel.get_pv(voxel2.id2) # get the proto-voxel representing the equivalence class
                self.painter.map_paint(pv, voxel2, flip=False)

                # --- paint the new bond if still necessary ---
                if self.paint_new_bond(bond1, bond2, "complementary"):
                    self.painter.map_paint(voxel2, pv, flip=False) # map back onto proto_voxel
                    continue
            
            # CASE 2: VOXEL NOT MAPPED YET
            sv, cv = self.mesovoxel.get_mesoparents(voxel2)
            pv, flip = None, False

            # map either flipping complementary bonds or not based on equivalence class
            # if touching sv, mesovoxel.add_comp_voxel(v2, sv)
            if voxel2.is_touching(sv.id2, type=2): 
                # if we need to add this to the mesovoxel
                if not self.mesovoxel.in_mesovoxel(-sv.id2, type=2):
                    self.mesovoxel.add_comp_voxel(voxel2, sv)
                    pv, flip = sv, True
                    self.add_uncolored_bonds(voxel2.bonds.values())

                self.painter.map_paint(sv, voxel2, flip=True)
                pv, flip = (cv, False) if cv else (sv, True)

            else: # if not touching its sv, map(sv -> v2)
                self.painter.map_paint(sv, voxel2, flip=False)
                pv, flip = sv, False
                voxel2.set_id2(sv.id2)

            # --- paint the new bond if still necessary ---
            if self.paint_new_bond(bond1, bond2, "complementary"):
                self.painter.map_paint(voxel2, sv, flip) # map back onto proto_voxel

    def map_lattice(self):
        """once we have a finalized mesovoxel, map the unique voxels onto the rest of the lattice"""
        for v in self.lattice.voxels:
            if self.mesovoxel.in_mesovoxel(v):
                continue
            # copy-pasting logic from comp_paint.CASE_2
            sv, cv = self.mesovoxel.get_mesoparents(v)
            if cv and v.is_touching(sv.id2, type=2):
                self.painter.map_paint(cv, v)
                v.set_id2(cv.id2)
            else:
                if v.is_touching(sv.id2, type=2):
                    self.painter.map_paint(sv, v, flip=True)
                    v.set_id2(-sv.id2)
                else:
                    self.painter.map_paint(sv, v)
                    v.set_id2(sv.id2)

    # def map_lattice2(self):
    #     """once we have a finalized mesovoxel, map the unique voxels onto the rest of the lattice"""
    #     for v in self.lattice.voxels:
    #         if self.mesovoxel.in_mesovoxel(v):
    #             continue
    #         # iterate through its partners to see which mesoparent to map
    #         sv, cv = self.mesovoxel.get_mesoparents(v)
            

                
    def paint_new_bond(self, bond1: Bond, bond2: Bond, type:str="structural") -> int:
        """paints the new color connecting bond1 and bond2 only if they're not none
        and also paints with self symmetries to exploit this new color
        
        returns 1 if success 0 if not"""
        # --- paint the new bond if still necessary ---
        if bond1.color is not None or bond2.color is not None:
            return 0

        self.n_colors += 1
        self.painter.paint_bonds(bond1, bond2, self.n_colors, type)

        # also paint with self-symmetries
        self.painter.self_sym_paint(bond1.voxel)
        self.painter.self_sym_paint(bond2.voxel)
        return 1
    
    def get_uncolored_bonds(self) -> list[Bond]:
        """get all uncolored bonds in the mesovoxe"""
        voxels = set(self.mesovoxel.all_voxels())
        bonds = set()
        bond_queue = []

        for v in voxels:
            voxel = self.lattice.get_voxel(v)
            for vertex, bond in voxel.bonds.items():
                if bond.color is None:
                    bond_queue.append(bond)
                    bonds.add((bond.voxel.id, vertex))
        
        return bond_queue
    
    def add_uncolored_bonds(self, bonds: list[Bond]):
        for b in bonds:
            if b.color is None and b not in self.seen_bonds:
                self.uncolored_bonds.append(b) 
                self.seen_bonds.add(b)