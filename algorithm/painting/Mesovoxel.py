from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Lattice import Lattice
from typing import Callable, Any

class Mesovoxel:
    def __init__(self, lattice: Lattice, has_symmetry: Callable[[Any, Any], tuple[bool, list]]):
        """
        Mesovoxel data structure, which is comprised of two sets
        
        (1) structural voxels:      clearly defined by symmetry alone
        (2) complementary voxels:   starts empty, and we add voxels to it
                                    1-by-1 as we paint bonds
        """
        # parent lattice/painter classes
        self.lattice = lattice
        self.has_symmetry = has_symmetry

        # these two sets uniquely define the mesovoxel
        # can be indexed with id2-1
        self.structural_voxels, self.adj_list = self.init_structural_voxels()
        self.complementary_voxels: list[int] = []
        
        self.init_structural_voxels()

    def init_structural_voxels(self) -> tuple[list[int], dict[int, list[int]]]:
        """
        Initialize a list of structural voxels based on the "lattice" attribute.
        Returns:
            structural_voxels: A set of voxel ids (ints) of structural voxels in lattice
            adj_list: the adjacency list mapping {id2: [v.id1, v.id1, ...]} 
                      where adj_list[id2][0] is the proto-voxel
        """
        # iterate over voxels
        voxels = iter(self.lattice.voxels)

        # init with first voxel in lattice
        v_0 = next(voxels)
        v_0.set_id2(1)

        # fill in the data structures with v_0
        structural_voxels = [v_0.id]
        adj_list = {}
        adj_list[1] = [v_0.id]
        
        i = 2
        for voxel in voxels:
            for sv in structural_voxels:
                has_sym, _ = self.has_symmetry(voxel, sv)
                if has_sym: # skip the else block if voxel has symmetry with something in sv
                    sv = self.lattice.get_voxel(sv)
                    adj_list[sv.id2].append(voxel.id)
                    break
            else:
                voxel.set_id2(i)
                structural_voxels.append(voxel.id)
                adj_list[i] = [voxel.id]
                i += 1

        return structural_voxels, adj_list
    

    def in_mesovoxel(self, voxel: Voxel|int, type=1) -> bool:
        """Returns whether the given voxel is in one of two mesovoxel sets or not."""
        if type==1:
            voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
            return voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels
        elif type==2:
            voxel_id = voxel.id2 if isinstance(voxel, Voxel) else voxel
            in_meso = self.adj_list.get(voxel_id)
            return True if in_meso else False

    def get_mesoparents(self, voxel: Voxel|int) -> list[Voxel, Voxel]:
        """
        Find the best parent voxel in the mesovoxel for the given voxel.
        Voxels satisfying this will either be added to the parent voxel's maplist
        or will become its complementary voxel. Requires no prior id2 information.

        Args:
            voxel (Voxel/int): Voxel to find mesoparent of
        Returns:
            mesoparents: [str_voxel, comp_voxel | None] 
            NOTE: should this return id1 or id2?
        """
        mesoparents = [None, None]

        #TODO: implement the less-naive way to find this
        # find the structural voxel with symmetry to the given voxel
        for s_voxel in self.structural_voxels:
            has_sym, _ = self.has_symmetry(s_voxel, voxel)
            if has_sym:
                mesoparents[0] = self.lattice.get_voxel(s_voxel)
                break

        # also find the complementary voxel
        for c_voxel in self.complementary_voxels:
            has_sym, _ = self.has_symmetry(c_voxel, voxel)
            if has_sym:
                mesoparents[1] = self.lattice.get_voxel(c_voxel)

        return mesoparents
    
    def get_pv(self, id2: int) -> Voxel:
        """given an id2, gets the corresponding proto-voxel"""
        v_id = self.adj_list[id2][0]
        return self.lattice.get_voxel(v_id)
    
    def add_comp_voxel(self, comp_voxel: Voxel, str_voxel: Voxel):
        """adds the comp_voxel for the specified str_voxel"""
        print(f"adding complementary voxel (id={comp_voxel.id}, id2={-str_voxel.id2})")
        id2 = -str_voxel.id2
        comp_voxel.set_id2(id2)

        # append the new comp_voxel to the data structures
        self.adj_list[id2] = [comp_voxel.id]
        if comp_voxel.id not in self.complementary_voxels:
            self.complementary_voxels.append(comp_voxel.id)

    def contains_voxel(self, voxel: Voxel|int):
        """
        Check if the the given voxel (id/Voxel) is mapped to a voxel in the Mesovoxel
        eg, whether the mesovoxel 'contains' the supplied voxel
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        return True if voxel_id in self.structural_voxels or voxel_id in self.complementary_voxels else False
    

    def all_voxels(self) -> list[int]:
        """
        Returns the set of all voxels in the mesovoxel. Aka just the current
        structural and complementary voxels.
        """
        return self.structural_voxels + self.complementary_voxels