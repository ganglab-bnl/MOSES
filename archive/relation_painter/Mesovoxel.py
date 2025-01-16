from algorithm.lattice.Voxel import Voxel
from archive.Lattice import Lattice
from algorithm.symmetry.Relation import Relation

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
        
@dataclass
class StructuralVoxel:
    """Wrapper around structural voxels for mesovoxel"""
    voxel: int
    complementary_voxel: Optional[int] = None

@dataclass
class ComplementaryVoxel:
    """Wrapper around complementary voxels for mesovoxel"""
    voxel: int
    structural_voxel: int


class Mesovoxel:
    def __init__(self, lattice: Lattice, painter):
        """
        Mesovoxel data structure, which is comprised a set of structural / complementary 
        voxels. 
            - The structural voxel set is defined clearly by symmetries alone
            - The complementary voxel set starts empty, and we add voxels to it 
              1-by-1 as we paint bonds.
        """
        self.painter = painter
        self.lattice = lattice
        self.mvoxels: list[MVoxel] = []
        self.voxels = {v.id: None for v in lattice.voxels} # None means there are no mvoxels assigned to it

        self.init_structural_voxels()

    def init_structural_voxels(self) -> set[int]:
        """
        Initialize a list of structural voxels based on the "lattice" attribute.
        Returns:
            s_voxels: A set of structural voxel ids
        """
        # init with first voxel in lattice
        structural_voxels = set([self.lattice.voxels[0].id]) 
        
        for voxel in self.lattice.voxels[1:]:
            
            # check if voxel has symmetry with any current structural_voxels
            symvoxels = self.lattice.symmetry_df.get_symvoxels(voxel.id)

            # if no symmetries, add voxel to structural_voxels!
            if not any(sv in structural_voxels for sv in symvoxels):
                structural_voxels.add(voxel.id) 
        
        # create new MVoxel instance for each structural voxel
        for i, s_voxel_id in enumerate(structural_voxels):
            self.voxels[s_voxel_id] = i
            mv = MVoxel(
                id=i,
                voxel=s_voxel_id,
                type="structural",
                mesovoxel=self
            )
            self.mvoxels.append(mv)

    def find_mesoparent(self, voxel) -> tuple[MVoxel, bool]:
        """
        Find the best parent voxel in the mesovoxel for the given voxel.
        Voxels satisfying this will either be added to the parent voxel's maplist
        or will become its complementary voxel.

        Args:
            voxel (Voxel/int): Voxel to find mesoparent of

        Returns:
            Case 1 (MVoxel, False): Mesoparent found, without negation
            Case 2 (MVoxel, True): Mesoparent found, with negation
            Case 3 (None, False): Mesoparent not found, N/A
        """
        voxel = voxel if isinstance(voxel, Voxel) else self.mesovoxel.lattice.get_voxel(voxel)
        negation_parent = None
        for mv in self.mvoxels:
            can_map, with_negation = mv.can_map(voxel)

            if can_map and not with_negation:
                return mv, with_negation
            
            # Note it down, but try to keep searching until we find non-negation
            if can_map and with_negation: 
                negation_parent = mv
            
        with_negation = True if negation_parent else False
        return negation_parent, with_negation

    
    def get_structural_voxels(self) -> list[MVoxel]:
        """Returns list of all structural MVoxels"""
        structural_voxels = []
        for mv in self.mvoxels:
            if mv.type == "structural":
                structural_voxels.append(mv)
        return structural_voxels

    def contains_voxel(self, voxel):
        """
        Check if the the given voxel (id/Voxel) is mapped to an MVoxel in the Mesovoxel
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        return True if self.voxels.get(voxel_id) else False
    

    def n_mvoxels(self):
        """Return the number of MVoxels in the mesovoxel"""
        return len(self.mvoxels)