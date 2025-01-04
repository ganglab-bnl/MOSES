from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Lattice2 import Lattice

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