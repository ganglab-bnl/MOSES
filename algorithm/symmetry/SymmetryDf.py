import numpy as np
import pandas as pd
import logging

from algorithm.lattice.Lattice import Lattice
from algorithm.lattice.Voxel import Voxel
from algorithm.symmetry.Rotation import NpRotationDict, ScipyRotationDict


class SymmetryDf:
    """
    Class which stores all combinations of voxel pairs and their symmetries.

    Attributes:
        - Lattice: Lattice object
        - Surroundings: Surroundings object
        - symmetry_operations: Dictionary of all possible symmetry operations
        - symmetry_df: pd.DataFrame object containing all voxel pairs and their symmetries
    
    Public:
        - symlist(v1, v2): Get the list of symmetries for a specific voxel pair v1 and v2
        - symdict(v): Get a dictionary of all possible non-empty symlists containing the voxel v 
                      eg, {sv: symlist(v, sv)}
        - symvoxels(v): Get list of all other voxels in lattice which voxel v has symmetry with
        - print_all_symdicts(): Print all possible symdicts for all voxels in the Lattice.MinDesign
    
    Internal:
        - _init_symmetry_df(): Initialize an empty symmetry_df with all possible voxel pairs and symmetry operations
        - _compute_all_symmetries(): Compute all possible symmetries between all 2-combinations of voxels
    """
    
    def __init__(self, lattice: Lattice):
        """
        Initialize the SymmetryDf object.
        """
        # Store references to lattice and Surroundings objects for use in symmetry comparisons
        self.lattice = lattice
        self.surroundings = lattice.surroundings

        # Create dictionary of all possible symmetry operations
        # Ex: {'90° X-axis': lambda x: np.rot90(x, 1, (0, 1)), ...}
        # self.symmetry_operations = NpRotationDict().all_rotations
        self.symmetry_operations = ScipyRotationDict().all_rotations
        
        # The SymmetryDf data structure containing all voxel pairs and their symmetries
        # Ex: (0, 1): {'90° X-axis': True, '180° Y-axis': False, ...}
        self.symmetry_df = self._init_symmetry_df()
        self._compute_all_symmetries2() # Fill all symmetries in place
    

    def symlist(self, voxel1, voxel2) -> list[str]:
        """
        Get the list of valid symmetries for a specific voxel pair.
        Returns an empty list if no symmetries are found.
        @param:
            - voxel1: Voxel or id (int) for the first voxel
            - voxel2: Voxel or id for the second voxel (can be the same as voxel1)
        @return:
            - symlist: List of symmetry labels that are valid for the voxel pair
                -> ex: ['90° X-axis', '180° Y-axis']
        """
        voxel1_id = voxel1 if isinstance(voxel1, int) else voxel1.id
        voxel2_id = voxel2 if isinstance(voxel2, int) else voxel2.id
        voxel_pair_label = VoxelPair.make_label(frozenset([voxel1_id, voxel2_id]))

        # Get those symmetries which are True for the voxel pair
        all_symmetries = self.symmetry_df.loc[voxel_pair_label]
        valid_symmetries = all_symmetries[all_symmetries == True].index
        symlist = list(valid_symmetries)

        return symlist
    
    def symdict(self, voxel) -> dict[str, list]:
        """
        Get a dictionary of all possible symlists containing the Voxel object

        Args:
            voxel: Voxel or id (int) to find all possible symlists for
        Returns:
            symdict: Dictionary of all voxel pairs with the given voxel 
                     which have symlists of non-zero length

        Examples:
        > symdict(voxel1)
        >   {0: ['90° X-axis', '180° Y-axis'],
             4: ['90° Z-axis', '270° X-axis']}
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        symdict = {}
        for voxel2 in self.lattice.voxels.values():
            current_symlist = self.symlist(voxel_id, voxel2.id)
            # only add symlists for voxel pairs with valid symmetries
            if len(current_symlist) > 0:
                # voxel_pair_label = VoxelPair.make_label(frozenset([id, voxel2.id]))
                symdict[voxel2.id] = current_symlist
        return symdict

    def get_symvoxels(self, voxel: int) -> list[int]:
        """
        Return a list of all other voxels in the lattice which the supplied voxel 
        has symmetry with

        Args:
            voxel: Voxel or id (int) of what voxel we want to get the symvoxels for
        """
        voxel_id = voxel.id if isinstance(voxel, Voxel) else voxel
        symdict = self.symdict(voxel_id)
        symvoxels = [sv for sv in symdict.keys()]
        return symvoxels
    
    # --- internal ---
    def _init_symmetry_df(self) -> pd.DataFrame:
        """
        Initialize an empty symmetry_df with all possible voxel pairs as the index, with 
        empty columns corresponding symmetry operations to be filled later.
        @return:
            - symmetry_df: pd.DataFrame object
        """
        # Create a list of all possible voxel pairs
        voxel_pairs_set = set()
        for voxel1 in self.lattice.voxels.values():
            for voxel2 in self.lattice.voxels.values():
                voxel_pairs_set.add(frozenset([voxel1.id, voxel2.id]))
        
        # Convert the set of frozensets to a list of formatted strings
        # E.g., "frozenset({0, 1})" -> "(0, 1)"
        sorted_voxel_pairs_set = sorted(voxel_pairs_set) # Sort lexicographically
        voxel_pairs = [VoxelPair.make_label(pair) for pair in sorted_voxel_pairs_set]

        # Create a dataframe containing True or False for each symmetry operation as the column names
        symmetry_df = pd.DataFrame(index=voxel_pairs, columns=self.symmetry_operations.keys())
        # symmetry_df = symmetry_df.fillna(None) # Fill NaN values with None

        return symmetry_df
    
    def _compute_all_symmetries(self):
        """
        Compute all possible symmetries between all 2-combinations of voxels
        in the Lattice.MinDesign. Fills self.symmetry_df in place with the results.
        """
        for sym_label, sym_function in self.symmetry_operations.items():

            # Loop through all possible voxel pairs
            for voxel1 in self.lattice.voxels:

                # Transform surroundings of voxel1 once per symmetry
                voxel1_surroundings = self.surroundings.voxel_surroundings(voxel1)
                transformed_voxel1_surroundings = sym_function(voxel1_surroundings)

                for voxel2 in self.lattice.voxels:
                    # Make voxel pair label (str) to index into SymmetryDf
                    voxel_pair_label = VoxelPair.make_label(frozenset([voxel1.id, voxel2.id])) 

                    # print(f'Checking symmetry for {voxel_pair_label} with {sym_label}...') # debug
    
                    symmetry_already_computed = not pd.isna(self.symmetry_df.loc[voxel_pair_label, sym_label])

                    if symmetry_already_computed:
                        continue # Symmetry already exists in symmetry_df

                    # Check symmetry:
                    # Two voxels are symmetric if their surroundings are the same after one is transformed
                    voxel2_surroundings = self.surroundings.voxel_surroundings(voxel2)
                    has_symmetry = np.array_equal(transformed_voxel1_surroundings, voxel2_surroundings) 

                    self.symmetry_df.loc[voxel_pair_label, sym_label] = has_symmetry # Store the result in symmetry_df

    def _compute_all_symmetries2(self):
        for sym_label, sym_function in self.symmetry_operations.items():

            # Loop through all possible voxel pairs
            for voxel1 in self.lattice.voxels.values():

                # Transform surroundings of voxel1 once per symmetry
                surr1 = self.surroundings.voxel_surroundings(voxel1)
                rot_surr1 = self.surroundings.rotate(surr1, sym_function)

                for voxel2 in self.lattice.voxels.values():
                    # Make voxel pair label (str) to index into SymmetryDf
                    voxel_pair_label = VoxelPair.make_label(frozenset([voxel1.id, voxel2.id])) 

                    # skip if symmetry has already been computed
                    symmetry_already_computed = not pd.isna(self.symmetry_df.loc[voxel_pair_label, sym_label])
                    if symmetry_already_computed:
                        continue 

                    # Check symmetry:
                    # Two voxels are symmetric if their surroundings are the same after one is transformed
                    surr2 = self.surroundings.voxel_surroundings(voxel2)
                    
                    if set(surr2.keys()) == set(rot_surr1.keys()):
                        has_symmetry = all(surr2[key] == rot_surr1[key] for key in surr2.keys())
                    else:
                        has_symmetry = False

                    self.symmetry_df.loc[voxel_pair_label, sym_label] = has_symmetry # Store the result in symmetry_df

    # info / print function
    def print_all_symdicts(self) -> None:
        """
        Auxiliary function to print all possible symdicts for all voxels in the Lattice.MinDesign
        (Not used in actual algorithm, only for testing)
        """
        for voxel in self.lattice.voxels.values():
            print(f'Voxel {voxel.id}\n---\nCoordinates: {voxel.coordinates} Material: {voxel.material}')
            print('Symmetries:')
            for voxel_pair, symlist in self.symdict(voxel.id).items():
                print(f'{voxel_pair}: {symlist}')
            print('\n')


class VoxelPair:
    """
    Helper class for managing the voxel pair labels for SymmetryDf.
    All methods use voxel.id to represent the Voxel objects.
    """
    def __init__(self):
        pass

    @staticmethod
    def make_label(voxel_pair: frozenset) -> str:
        """
        Convert frozenset to string for use in representing voxel pairs in SymmetryDf
        E.g., "frozenset({0, 1})" -> "(0, 1)"

        @param:
            - voxel_pair: a frozenset of two voxel.id values
        @return:
            - string: str, "(voxel1.id, voxel2.id)"
        """
        # Convert to sorted list for consistency
        sorted_pair_list = sorted(voxel_pair) 
        # Convert each integer in list to str, join with ", ", then wrap in parentheses
        label = "(" + ", ".join(map(str, sorted_pair_list)) + ")" 
        return label

    @staticmethod
    def get_voxels(label: str) -> list:
        """
        Return the two(or one) Voxel.id values in the VoxelPair object
        @param:
            - label: str, "(voxel1.id, voxel2.id)" or "(voxel1.id)"
        @return:
            - voxel1, voxel2: list of ints, [voxel1.id, voxel2.id] or [voxel1.id]
        """
        # Remove parentheses and split by ", " to get a list of strings
        voxel_strings = label[1:-1].split(", ")
        voxels = map(int, voxel_strings)
        return list(voxels)
    
    @staticmethod
    def get_partner(label: str, voxel_id: int) -> int:
        """Get the partner Voxel.id from the label"""

        voxel_pair = VoxelPair.get_voxels(label)

        if voxel_id not in voxel_pair:
            logging.error(f"Voxel {voxel_id} not in VoxelPair {label}")
            return None

        if len(voxel_pair) == 1:
            return voxel_id # Represents self-symmetry
        
        # Two voxels in the the pair
        voxel1_id, voxel2_id = voxel_pair
        return voxel2_id if voxel_id == voxel1_id else voxel1_id
    


    
