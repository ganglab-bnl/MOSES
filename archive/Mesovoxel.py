from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Lattice import Lattice

from dataclasses import dataclass
from typing import Optional


class MVoxel:
    def __init__(self, id: int, voxel, type: str, mesovoxel: 'Mesovoxel', mesopartner: 'MVoxel'=None):
        """
        Initialize the MVoxel with the initial voxel prototype
        
        Args:
            voxel: The initial voxel prototype to define the equivalence class
            type: Whether this voxel is 'structural' or 'complementary'
            mesovoxel: The parent mesovoxel instance this MVoxel is associated with
            mesopartner: The associated complementary / structural voxel in the pair (if it exists)
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel

        # MVoxel attributes
        self.id = id
        self.maplist = set([voxel_id])
        self.type = type   # structural or complementary
        self.mesopartner = mesopartner   # its corresponding str/comp Mvoxel

        # reference to its parent mesovoxel
        self.mesovoxel = mesovoxel

    def add_voxel(self, voxel) -> set[int]:
        """
        Adding new voxel to self.maplist and updating rest of voxels
        with new info. Also adds to mesovoxel.voxels!
        """
        voxel = voxel.id if isinstance(voxel, Voxel) else voxel

        painted_voxels = self.update_voxels(voxel=voxel, with_negation=False)
        self.mesovoxel.voxels[voxel] = self.id
        return painted_voxels

    def update_voxels(self, voxel, with_negation: bool) -> set[int]:
        """
        Updates all voxels in self.maplist with new voxel's bond information.
        Called when adding new c_voxel as its partner or vice-versa
        """
        voxel = voxel if isinstance(voxel, Voxel) else self.mesovoxel.lattice.get_voxel(voxel)
        painted_voxels = set()
        for mv in self.maplist:
            symlist = self.mesovoxel.lattice.symmetry_df.symlist(voxel.id, mv)
            
            if symlist is None or len(symlist) == 0:
                continue # maybe throw error?

            # might need specific sym - if so, address later w/ more info
            # jason said he only uses the first symmetry too so 🤷‍♀️
            pv = self.mesovoxel.painter.map_paint(parent=voxel, child=mv, sym_label=symlist[0], with_negation=with_negation) 
            painted_voxels.update(pv)
        
        return painted_voxels


    def set_mesopartner(self, voxel):
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        self.mesopartner = voxel_id

    def can_map(self, voxel) -> tuple[bool, bool]:
        """
        Checks if a voxel can map to this Mvoxel, and whether 
        it's only with negation
        
        Returns
            can_map, with_negation (bool, bool)
        """
        voxel = voxel if isinstance(voxel, Voxel) else self.mesovoxel.lattice.get_voxel(voxel)
        mv = next(iter(self.maplist)) # Prop: All mv in maplist have the same bonds
        mv = self.mesovoxel.lattice.get_voxel(mv)
        symlist = self.mesovoxel.lattice.symmetry_df.symlist(voxel.id, mv.id)

        # has no symmetry, should be only case where we can't map in some way
        if symlist is None or len(symlist) == 0:
            return False, False

        found_equal = False
        for sym_label in symlist:
            rel = Relation.get_voxel_relation(voxel, mv, sym_label)
            # print(f"Relation ({rel}) between Voxel {voxel.id} and {self} with sym={sym_label}")
            
            # Mapping logic based on the voxel-voxel relation
            if rel == "no relation":
                return False, False
            elif rel == "negation":
                return True, True
            elif rel == "equal":
                found_equal = True

        if found_equal:
            return True, False
        
        else: # all loose - not enough information to map it onto this MVoxel
            return False, False


    def __str__(self):
        mesopartner_id = None if not self.mesopartner else self.mesopartner.id
        return (f"MVoxel(id={self.id}, type={self.type}, "
                f"mesopartner={mesopartner_id}, maplist={list(self.maplist)})")
    
    def repr_voxel(self) -> Voxel:
        """Get a representative voxel for the MVoxel"""
        voxel_id = next(iter(self.maplist))
        return self.mesovoxel.lattice.get_voxel(voxel_id)

class Mesovoxel:
    def __init__(self, lattice: Lattice, painter):
        """
        Mesovoxel data structure, which is comprised of two sets
        
        (1) structural voxels:      clearly defined by symmetry alone
        (2) complementary voxels:   starts empty, and we add voxels to it
                                    1-by-1 as we paint bonds
        """
        # parent lattice/painter classes
        self.painter = painter
        self.lattice = lattice

        # these two sets uniquely define the mesovoxel
        self.structural_voxels: set[int] = self.init_structural_voxels()
        self.complementary_voxels: set[int] = set([])
        
        self.init_structural_voxels()

    def init_structural_voxels(self) -> set[int]:
        """
        Initialize a list of structural voxels based on the "lattice" attribute.
        Returns:
            structural_voxels: A set of voxel ids (ints) of structural voxels in lattice
        """
        # iterate over voxels
        voxels = iter(self.lattice.voxels.values())

        # init with first voxel in lattice
        v_0 = next(voxels)
        v_0.set_type("structural")
        structural_voxels = set([v_0.id]) 
        
        for voxel in voxels:
            # check if voxel has symmetry with any current structural_voxels
            symvoxels = self.lattice.symmetry_df.get_symvoxels(voxel.id)

            # if no symmetries, add voxel to structural_voxels!
            if not any(sv in structural_voxels for sv in symvoxels):
                voxel.set_type("structural")
                structural_voxels.add(voxel.id)

        return structural_voxels
    

    def in_mesovoxel(self, voxel) -> bool:
        """Returns whether the given voxel is in one of two mesovoxel sets or not."""
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        return voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels

    def find_mesoparent(self, voxel) -> dict[str, int]:
        """
        Find the best parent voxel in the mesovoxel for the given voxel.
        Voxels satisfying this will either be added to the parent voxel's maplist
        or will become its complementary voxel.

        Args:
            voxel (Voxel/int): Voxel to find mesoparent of

        Returns:
            mesoparents: dict {"structural": voxel.id, "complementary": voxel.id}
        """
        mesoparents = dict()

        # find all s_voxels with symmetry to the given voxel
        for s_voxel in self.structural_voxels:
            symlist = self.lattice.symmetry_df.symlist(voxel, s_voxel)
            if len(symlist) > 0:
                mesoparents["structural"] = s_voxel

        # also go thru c voxels
        for c_voxel in self.complementary_voxels:
            symlist = self.lattice.symmetry_df.symlist(voxel, c_voxel)
            if len(symlist) > 0:
                mesoparents["complementary"] = c_voxel

        return mesoparents


    def contains_voxel(self, voxel):
        """
        Check if the the given voxel (id/Voxel) is mapped to an MVoxel in the Mesovoxel
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        return True if voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels else False
    

    def all_voxels(self) -> list[int]:
        """
        Returns the set of all voxels in the mesovoxel. Aka just the current
        structural and complementary voxels.
        """
        return self.structural_voxels | self.complementary_voxels