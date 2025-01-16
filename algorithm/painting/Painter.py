from copy import deepcopy

from algorithm.lattice.Voxel import Voxel
from algorithm.lattice.Bond import Bond
from algorithm.lattice.Lattice import Lattice
from algorithm.symmetry.Rotation import Rotater
from algorithm.painting.Mesovoxel import Mesovoxel


class Painter:
    def __init__(self, lattice: Lattice, verbose=False):
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
        # Data structures (class composition!)
        self.lattice = lattice
        self.mesovoxel = Mesovoxel(lattice, self)

        # Count of total # colors (not including complementary) 
        # used to paint the MinDesign
        self.n_colors = 0 

        # Rotater instance (used for map painting)
        self.rotater = Rotater(lattice)
        self.verbose: bool = verbose # If true, prints debugging statements

    def paint_lattice(self):
        """Final callable method to paint the lattice."""
        self.str_paint_lattice()
        self.comp_paint_lattice()
        self.map_mesovoxel()

    def str_paint_lattice(self):
        """
        Phase 1: Paint initial set of structural bonds in the lattice.
        Just paint a path of structural bonds connecting all structural voxels
        to each other.
        """
        if self.verbose:
            print("===== STARTING STR_PAINT_LATTICE =====")
        for s_voxel_id in self.mesovoxel.structural_voxels:
            s_voxel = self.lattice.get_voxel(s_voxel_id)

            for direction, bond in s_voxel.bond_dict.dict.items():
                partner_voxel, partner_bond = s_voxel.get_partner(direction)

                # --- Paint path of structural bonds ---
                # ensure neither bond is colored yet
                if bond.color is not None or partner_bond.color is not None:
                    continue
                # only want to paint bonds between two structural voxels
                if partner_voxel.type != "structural":
                    continue
                
                # Paint the new bond
                self.n_colors += 1
                self.paint_bond(bond, self.n_colors, 'structural')
                self.paint_bond(partner_bond, -1*self.n_colors, 'structural')

                if self.verbose:
                    print(f"\n--- PAINT S_BOND ({self.n_colors}) --- \nvoxel_{s_voxel_id} ({bond.direction}) <---> voxel_{partner_voxel.id} ({partner_bond.direction})")

                self.self_sym_paint(s_voxel)
                self.self_sym_paint(partner_voxel)


    def comp_paint_lattice(self):
        """
        Paint all complementary bonds, slowly adding complementary voxels into the mesovoxel
        until all vertices on the structural voxel set are painted.
        """

        if self.verbose:
            print("\n===== STARTING COMP_PAINT_LATTICE =====\n")
        count = 0
        for voxel1_id in self.mesovoxel.structural_voxels:
            voxel1 = self.lattice.get_voxel(voxel1_id)
            for direction1, bond1 in voxel1.bond_dict.dict.items():

                # skip bonds which are already painted
                if bond1.color is not None:
                    continue
                
                # get the voxel which the structural voxel is connected to
                bond2 = bond1.bond_partner
                voxel2 = bond2.voxel

                # if count==1:
                #     return
                if self.verbose:
                    print(f"\nLOOP {count}: Between voxel1 ({voxel1_id})'s bond {bond1.get_label()} and voxel2 ({voxel2.id})'s bond {bond2.get_label()}\n---")
                count += 1

                # check what mesoparent it has
                mesoparents = self.mesovoxel.find_mesoparent(voxel2)
                # unpack
                comp_mp = mesoparents.get("complementary")
                str_mp = mesoparents.get("structural")
            
                # if there is a c_voxel in the mesovoxel which looks like voxel2
                if comp_mp:
                    if self.verbose:
                        print(f"MESOPARENT: Found comp_mp {comp_mp}!")
                    symlist = self.lattice.symmetry_df.symlist(voxel2, comp_mp) # take any valid sym
                    for sym in symlist:
                        res = self.map_paint(parent=comp_mp, child=voxel2, sym_label=sym) # use it to map
                        if res==0:
                            res = self.map_paint(parent=comp_mp, child=voxel2, sym_label=sym, with_negation=True) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break
                    
                    if bond1.color is None and bond2.color is None:
                        self.n_colors += 1

                        symlist = self.lattice.symmetry_df.symlist(voxel1, voxel2)
                        if symlist==[] or symlist is None:
                            bond_type = "structural"
                        else:
                            bond_type = "complementary"

                        # paint the bond
                        if self.verbose:
                            print(f"\n--- PAINT {bond_type} BOND ({self.n_colors}) --- \nvoxel_{voxel1.id} ({bond1.direction}) <---> voxel_{voxel2.id} ({bond2.direction})\n")
                    
                        self.paint_bond(bond=bond1, color=self.n_colors, type=bond_type)
                        self.paint_bond(bond=bond2, color=-self.n_colors, type=bond_type)

                    # paint self symmetries
                    self.self_sym_paint(voxel1)
                    self.self_sym_paint(voxel2)

                    # map the child back onto the parent
                    if self.verbose:
                        print(f"mapping child voxel_{voxel2.id} back onto parent voxel_{comp_mp}")
                    for sym in symlist:
                        res = self.map_paint(parent=voxel2, child=comp_mp, sym_label=sym) # use it to map
                        if res==0:
                            res = self.map_paint(parent=voxel2, child=comp_mp, sym_label=sym, with_negation=True) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break

                elif str_mp == voxel1_id: # only s_voxel found and it's voxel1
                    if self.verbose:
                        print(f"MESOPARENT: Only found str_mp {str_mp} and it IS voxel1. Flipping complementarity when mapping.")
                    # flip the complementarity when mapping and add it to complementary set
                    symlist = self.lattice.symmetry_df.symlist(voxel2, str_mp)
                    for sym in symlist:
                        res = self.map_paint(parent=str_mp, child=voxel2, sym_label=sym, with_negation=True) # use it to map
                        if res==0:
                            res = self.map_paint(parent=str_mp, child=voxel2, sym_label=sym, with_negation=True) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break

                    if bond1.color is None and bond2.color is None:
                        # paint the bond
                        self.n_colors += 1

                        symlist = self.lattice.symmetry_df.symlist(voxel1, voxel2)
                        if symlist==[] or symlist is None:
                            bond_type = "structural"
                        else:
                            bond_type = "complementary"

                        # paint the bond
                        if self.verbose:
                            print(f"\n--- PAINT {bond_type} BOND ({self.n_colors}) --- \nvoxel_{voxel1.id} ({bond1.direction}) <---> voxel_{voxel2.id} ({bond2.direction})\n")
                    
                        self.paint_bond(bond=bond1, color=self.n_colors, type=bond_type)
                        self.paint_bond(bond=bond2, color=-self.n_colors, type=bond_type)

                    # add the voxel to the complementary set
                    voxel2.set_type("complementary")
                    self.mesovoxel.complementary_voxels.add(voxel2.id)
                    
                    # paint self symmetries
                    self.self_sym_paint(voxel1)
                    self.self_sym_paint(voxel2)

                    # map the child back onto the parent
                    # self.map_paint(parent=voxel2, child=str_mp, sym_label=sym, with_negation=True)
                    if self.verbose:
                        print(f"mapping child voxel_{voxel2.id} back onto parent voxel_{str_mp}")
                    for sym in symlist:
                        res = self.map_paint(parent=voxel2, child=str_mp, sym_label=sym, with_negation=True) # use it to map
                        if res==0:
                            res = self.map_paint(parent=voxel2, child=str_mp, sym_label=sym, with_negation=False) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break


                else: # only a s_voxel and it's not voxel1
                    if self.verbose:
                        print(f"MESOPARENT: Only found str_mp {str_mp} and it's not voxel1. (No flip comp)")
                    symlist = self.lattice.symmetry_df.symlist(voxel2, str_mp)
                    
                    for sym in symlist:
                        res = self.map_paint(parent=str_mp, child=voxel2, sym_label=sym) # use it to map
                        if res==0:
                            res = self.map_paint(parent=str_mp, child=voxel2, sym_label=sym, with_negation=True) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break
                    
                    if bond1.color is None and bond2.color is None:
                        # paint the bond
                        self.n_colors += 1

                        symlist = self.lattice.symmetry_df.symlist(voxel1, voxel2)
                        if symlist==[] or symlist is None:
                            bond_type = "structural"
                        else:
                            bond_type = "complementary"

                        # paint the bond
                        if self.verbose:
                            print(f"\n--- PAINT {bond_type} BOND ({self.n_colors}) --- \nvoxel_{voxel1.id} ({bond1.direction}) <---> voxel_{voxel2.id} ({bond2.direction})\n")
                    
                        self.paint_bond(bond=bond1, color=self.n_colors, type=bond_type)
                        self.paint_bond(bond=bond2, color=-self.n_colors, type=bond_type)
                    
                    # paint self symmetries
                    self.self_sym_paint(voxel1)
                    self.self_sym_paint(voxel2)

                    # map the child back onto the parent
                    # self.map_paint(parent=voxel2, child=str_mp, sym_label=sym)
                    if self.verbose:
                        print(f"mapping child voxel_{voxel2.id} back onto parent voxel_{str_mp}")
                    for sym in symlist:
                        res = self.map_paint(parent=voxel2, child=str_mp, sym_label=sym) # use it to map
                        if res==0:
                            res = self.map_paint(parent=voxel2, child=str_mp, sym_label=sym, with_negation=True) # try it negated
                        if res==1: # break out of loop if we successfully painted
                            break

                    
    def map_mesovoxel(self) -> None:
        """
        Map the voxels in the mesovoxel back onto all voxels in the lattice.
        To make the visuals look nicer.
        """
        if self.verbose:
            print("Mapping the mesovoxel onto the rest of the lattice...\n---")
        for voxel1 in self.lattice.voxels.values():
            
            # skip voxels that are in the mesovoxel
            if self.mesovoxel.contains_voxel(voxel1):
                if self.verbose:
                    print(f"skipping {voxel1.id}, already in mesovoxel")
                continue

            # check what mesoparent it has
            mesoparents1 = self.mesovoxel.find_mesoparent(voxel1)
            # unpack
            comp_mp = mesoparents1.get("complementary")
            str_mp = mesoparents1.get("structural")

            # if only str_mp exists, then only one choice to map onto voxel1
            if not comp_mp:
                if self.verbose:
                    print(f"only str_mp {str_mp} exists, mapping onto voxel {voxel1.id}")
                symlist = self.lattice.symmetry_df.symlist(str_mp, voxel1)
                for sym in symlist:
                    res = self.map_paint(parent=str_mp, child=voxel1, sym_label=sym, with_negation=False, force=False)
                    if res:
                        break
                voxel1.set_type("structural")
                continue # skip rest of loop

            # if comp_mp exists, go through all neighbors until we know
            # which variant to map
            map_variant = str_mp
            mesotype1 = "structural"
            for bond in voxel1.bond_dict.dict.values():
                voxel2 = bond.get_partner_voxel()
                if self.verbose:
                    print(f"checking partner {voxel2.id}")

                # skip the partner voxel if it has no symmetry with voxel1
                symlist = self.lattice.symmetry_df.symlist(voxel1, voxel2)
                if symlist == [] or symlist is None:
                    continue
                
                # find which variant to map it based on the type of the partner voxel
                mesotype2 = voxel2.get_type()
                if self.verbose:
                    print(f"{voxel2.id} has sym and mesotype {mesotype2}")
                if mesotype2 == "structural":
                    map_variant = comp_mp
                    mesotype1 = "complementary"
                    if self.verbose:
                        print(f"found partner voxel{voxel2.id} with type {mesotype2} - setting map_variant to {comp_mp}")
                    break
                elif mesotype2 == "complementary":
                    map_variant = str_mp
                    mesotype1 = "structural"
                    if self.verbose:
                        print(f"found partner voxel{voxel2.id} with type {mesotype2} - setting map_variant to {str_mp}")
                    break
                else:
                    continue
            
            if self.verbose:
                print(f"both str_mp {str_mp} and comp_mp {comp_mp} exist, mapping {map_variant} onto voxel {voxel1.id}")
            sym = self.lattice.symmetry_df.symlist(map_variant, voxel1)[0]
            res = self.map_paint(parent=map_variant, child=voxel1, sym_label=sym, force=False)
            voxel1.set_type(mesotype1)
                

    def self_sym_paint(self, voxel) -> None:
        """Paint a given voxel with all its self symmetries"""
        # handle Voxel and int (voxel.id) instances
        voxel = voxel if isinstance(voxel, Voxel) else self.lattice.get_voxel(voxel)

        if self.verbose:
            print(f"self-sym paint(voxel_{voxel.id})")

        symlist = self.lattice.symmetry_df.symlist(voxel.id, voxel.id)
        for sym_label in symlist:
            _ = self.map_paint(parent=voxel, child=voxel, sym_label=sym_label)

    def map_paint(self, parent, child, sym_label: str, with_negation: bool=False, force=False) -> int:
        """
        Map the bonds of a parent voxel onto the child voxel, with some symmetry operation.
        Throws an error 0 if the map painting operation results in a bad paint, else 1.
        
        Args:
            parent: Voxel or id corresponding to voxel with bond info to map
            child: Voxel or id for voxel as target of mapping
            sym_label (str): Label of rotation to apply to parent voxel before mapping onto child

        Returns:
            int, 0 for fail and 1 for success
        """
        parent = parent if isinstance(parent, Voxel) else self.lattice.get_voxel(parent)
        child = child if isinstance(child, Voxel) else self.lattice.get_voxel(child)
        
        if self.verbose:
            print(f"    map_paint(parent_{parent.id} --> child_{child.id}, sym={sym_label}, with_negation={with_negation})")
            print(f"        parent = {[f'{b.get_label()} ({b.color}),' for b in parent.bond_dict.dict.values()]}")
            print(f"        child = {[f'{b.get_label()} ({b.color}),' for b in child.bond_dict.dict.values()]}")

        rotated_parent = self.rotater.rotate_voxel(voxel=parent, rot_label=sym_label) # rotated bond_dict object

        # store copies of original bonddicts incase it fails
        og_child_bd = deepcopy(child.bond_dict.dict)
        og_parent_bd = deepcopy(parent.bond_dict.dict) 

        # Go through and map each parent bond to the child on its corresponding (rotated) vertex
        for direction, parent_bond in rotated_parent.dict.items():
            child_bond = child.bond_dict.get_bond(direction)

            # no need to paint None colors)
            if parent_bond.color is None:
                if self.verbose:
                    print(f"oops! parent bond {parent_bond.get_label()} is none")
                continue
            # only paint onto already-painted bonds if force is true
            if child_bond.color is not None and not force:
                if self.verbose:
                    print(f"oops! child bond {child_bond.get_label()} is not none, and we're not forcing")
                continue
            
            # Bond color is negated (on c_bonds) if with_negation
            neg = -1 if with_negation and parent_bond.type == "complementary" else 1
            bond_color = int(neg * parent_bond.color)

            # PALINDROMIC CHECK before we paint
            if child.is_palindromic(bond_color) or child_bond.bond_partner.voxel.is_palindromic(-1*bond_color):
                # undo any painting changes
                child.bond_dict.dict = og_child_bd
                parent.bond_dict.dict = og_parent_bd
                if self.verbose:
                    print("Mapping failed.")
                return 0 # fail
                
            self.paint_bond(child_bond, bond_color, type=parent_bond.type)
            bond_partner = child_bond.bond_partner
            self.paint_bond(bond_partner, -1*bond_color, type=parent_bond.type)

        return 1 # success

    def paint_bond(self, bond: Bond, color: int, type: str) -> None:
        """
        Paint certain color / type onto a bond.
        
        Args:
            bond (Bond): The bond object to paint
            color (int): What color to paint it
            type (str): Either "complementary" or "structural" depending on type of bond to paint
        """
        if self.verbose:
            print(f"\t ---> painting {color} onto voxel {bond.voxel.id}'s bond {bond.get_label()} with type {type} ")
        bond.set_color(color)
        bond.set_type(type)