
from algorithm.lattice.Lattice import Lattice
from algorithm.symmetry.SymmetryDf import SymmetryDf
from algorithm.symmetry.Rotation import RotationDict
from algorithm.lattice.Voxel import Bond

class Painter:
    def __init__(self, lattice: Lattice, symmetry_df: SymmetryDf):
        """
        The idea is to create a coloring scheme for the lattice which minimizes 
        the total number of unique origami and number of colors.
        
        Constraints:
            1. Color complementarity: All colors(+) must be binded to its complement(-)
            2. No palindromes: A color(+) and its complement(-) cannot exist on the same voxel

        Note!
            Following from constraint 1, each painting operation (specifically self_sym_paint)
            also modifies the binding of its partner. Thus we return the painted_voxels after
            each painting so we can exploit each color as much as we can.
        """
        # important data structure references
        self.lattice = lattice
        self.symmetry_df = symmetry_df
        self.rot_dict = RotationDict()

        # count of total # colors (not including complementary)
        # used to color the mesovoxel
        self.n_colors = 0

    def self_sym_paint(self, voxel):
        """paint the voxel with its own self symmetries"""
        self.map_paint(voxel, voxel)

    def map_paint(self, parent, child, flip=False):
        """
        map all of the parent symmetries onto the child. 
        returns 1 on success, 0 on failure (palindromic error)

        NOTE: is equivalent to mapping a single symmetry and then painting
        the child with its own self symmetries
        """
        parent = self.lattice.get_voxel(parent)
        child = self.lattice.get_voxel(child)

        # preemptive check to see if mapping would cause a palindromic error
        if self.is_palindromic(parent.bonds, child.bonds, flip):
            return 0

        symlist = self.symmetry_df.symlist(parent, child)

        for sym in symlist:
            # rotate parent voxel
            rotated_parent_bonds = self.rot_dict.rotate_bonds(parent.bonds, sym)
            self._map_bonds(rotated_parent_bonds, child.bonds, flip)
        
        return 1

    def _map_bonds(self, parent_bonds: dict[tuple[int, int, int], Bond], 
                   child_bonds: dict[tuple[int, int, int], Bond], flip=False) -> None:
        """handles the nitty gritty in mapping bonds from v1-->v2
        returns 1 if success, 0 if failure
        """
        for coords, parent_bond in parent_bonds.items():
            child_bond = child_bonds[coords]

            # don't map None-colored bonds, or onto already-painted bonds
            if parent_bond.color is None or child_bond.color is not None:
                continue
            
            # negate bond colors on complementary bonds if flip==True
            neg = -1 if flip and parent_bond.type == "complementary" else 1
            color = int(neg * parent_bond.color)
            self.paint_bonds(child_bond, child_bond.partner, color, parent_bond.type)


    def is_palindromic(self,  parent_bonds: dict[tuple[int, int, int], Bond], 
                   child_bonds: dict[tuple[int, int, int], Bond], flip=False) -> int:
        """a PALINDROMIC CHECK before we paint. 
        due to experimental constraints, we want to avoid having both a 
        color and its complement on the same voxel.
        
        returns 1 if palindromic else 0 (good)
        """
        for pb in parent_bonds.values():
            if pb.color is None: 
                continue # no need to check None bonds

            # create the mappable color wrt. whether it would be flipped or nah
            neg = -1 if flip and pb.type=="complementary" else 1
            mappable_color = int(neg * pb.color)

            # check all child bonds to see if the potentially mappable color 
            # would create a palindromic error
            for cb in child_bonds.values():
                if cb.color is None:
                    continue
                if cb.color==-1*mappable_color or cb.partner.color==mappable_color:
                    return 1 # is palindromic (bad)
                
        return 0 # is not palindromic (good!)
        
    def paint_bonds(self, bond1: Bond, bond2: Bond, color: int, type: str) -> None:
        """paint a certain color + type onto a bond (bond1) and its partner (bond2)
        
        Args:
            color (int): what color to paint it, negative = complementary to its positive
            type (str): either "complementary" or "structural" depending on whether its between
                        two structurally unique voxels or not
        """
        bond1.set_color(color)
        bond1.set_type(type)
        bond2.set_color(-color)
        bond2.set_type(type)