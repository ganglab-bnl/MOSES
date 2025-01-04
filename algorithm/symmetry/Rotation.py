import numpy as np
from scipy.spatial.transform import Rotation as R

from algorithm.lattice.Bond import Bond, BondDict
from algorithm.lattice.Voxel import Voxel

class NpRotationDict:
    """
    Class to initialize and manage all (numpy) rotation transformations
    for use in Surroundings.
    """

    def __init__(self):

        # Initialize dictionaries for transformation functions
        self.translation = {
            'translation': lambda x: x # Identity function
        }

        # self.single_rotations = {
        #     '90° X-axis': lambda x: np.rot90(x, 1, (0, 2)),
        #     '180° X-axis': lambda x: np.rot90(x, 2, (0, 2)),
        #     '270° X-axis': lambda x: np.rot90(x, 3, (0, 2)),
        #     '90° Y-axis': lambda x: np.rot90(x, 1, (0, 1)),  
        #     '180° Y-axis': lambda x: np.rot90(x, 2, (0, 1)),  
        #     '270° Y-axis': lambda x: np.rot90(x, 3, (0, 1)),  
        #     '90° Z-axis': lambda x: np.rot90(x, 1, (1, 2)),
        #     '180° Z-axis': lambda x: np.rot90(x, 2, (1, 2)),
        #     '270° Z-axis': lambda x: np.rot90(x, 3, (1, 2))
        # }

        # Axes
        # 0 = Z
        # 1 = Y
        # 2 = X
        self.single_rotations = {
            # Rotations around the X-axis
            '90° X-axis': lambda x: np.rot90(x, 1, (1, 0)),
            '180° X-axis': lambda x: np.rot90(x, 2, (1, 0)),
            '270° X-axis': lambda x: np.rot90(x, 3, (1, 0)),

            # Rotations around the Y-axis
            '90° Y-axis': lambda x: np.rot90(x, 1, (0, 2)),  
            '180° Y-axis': lambda x: np.rot90(x, 2, (0, 2)),  
            '270° Y-axis': lambda x: np.rot90(x, 3, (0, 2)), 

            # Rotations around the Z-axis
            '90° Z-axis': lambda x: np.rot90(x, 1, (1, 2)),
            '180° Z-axis': lambda x: np.rot90(x, 2, (1, 2)),
            '270° Z-axis': lambda x: np.rot90(x, 3, (1, 2))
        }
        self.double_rotations = self._init_double_rotations()
        self.all_rotations = {
            **self.translation, 
            **self.single_rotations, 
            **self.double_rotations
        }

    def get_rotation(self, rot_label: str):
        """
        Get the rotation function based on the label (ex: '90° X-axis', '180° Y-axis', etc.)
        """
        return self.all_rotations[rot_label]

    def _init_double_rotations(cls):
        """
        Initialize double_rotations to contain all possible combinations of single_rotations,
        but excluding double rotations on the same axis.
        @return:
            - double_rotations: Dictionary of lambda functions for double rotations
                                {"label1 + label2": lambda x: rotation2(rotation1(x))}
        """
        frozen_double_rotations = [] # List to store frozensets of double rotations (avoids duplicates)

        for label1 in cls.single_rotations.keys():
            for label2 in cls.single_rotations.keys():
                # Create a frozen set of the pair of rotation labels
                rotation_pair = frozenset([label1, label2])

                # Get the last word in string (the axis) from each rotation label
                rotation1_axis = label1.split(' ')[-1] 
                rotation2_axis = label2.split(' ')[-1]

                # Only consider double rotation if they are on different axes and not already considered
                if rotation1_axis != rotation2_axis and rotation_pair not in frozen_double_rotations:
                    frozen_double_rotations.append(rotation_pair)
        
        # Iterate through list of non-repeating double rotations and create a dictionary of lambda functions
        double_rotations = {}
        for rotation_pair in frozen_double_rotations:
            label1, label2 = rotation_pair
            rotation1, rotation2 = cls.single_rotations[label1], cls.single_rotations[label2]

            double_rotations[f'{label1} + {label2}'] = \
                        lambda x, rotation1=rotation1, rotation2=rotation2: rotation2(rotation1(x))
            
        # Sort the dictionary by key
        sorted_double_rotations = {key: double_rotations[key] for key in sorted(double_rotations)}
        return sorted_double_rotations
    

class ScipyRotationDict:
    """
    Class for (scipy) rotations for transforming the vertices based on euclidean 
    coordinate space. For use in BondPainter.
    """

    def __init__(self):
        self.translation = {
            'translation': lambda x: x # Identity function
        }
        self.single_rotations = {
            '90° X-axis': lambda x: R.from_euler('x', 90, degrees=True).apply(x),
            '180° X-axis': lambda x: R.from_euler('x', 180, degrees=True).apply(x),
            '270° X-axis': lambda x: R.from_euler('x', 270, degrees=True).apply(x),
            '90° Y-axis': lambda x: R.from_euler('y', 90, degrees=True).apply(x),
            '180° Y-axis': lambda x: R.from_euler('y', 180, degrees=True).apply(x),
            '270° Y-axis': lambda x: R.from_euler('y', 270, degrees=True).apply(x),
            '90° Z-axis': lambda x: R.from_euler('z', 90, degrees=True).apply(x),
            '180° Z-axis': lambda x: R.from_euler('z', 180, degrees=True).apply(x),
            '270° Z-axis': lambda x: R.from_euler('z', 270, degrees=True).apply(x)
        }
        self.double_rotations = self._init_double_rotations()
        self.all_rotations = {
            **self.translation,
            **self.single_rotations,
            **self.double_rotations
        }

    def get_rotation(self, rot_label: str):
        """
        Get the rotation function based on the label (ex: '90° X-axis', '180° Y-axis', etc.)
        """
        if rot_label not in self.all_rotations:
            raise ValueError(f"Invalid rotation label: {rot_label}")
        
        return self.all_rotations.get(rot_label)
    
    def _init_double_rotations(self):
        """
        Initialize double_rotations to contain all possible combinations of single_rotations,
        but excluding double rotations on the same axis.
        @return:
            - double_rotations: Dictionary of lambda functions for double rotations
                                {"label1 + label2": lambda x: rotation2(rotation1(x))}
        """
        frozen_double_rotations = [] # List to store frozensets of double rotations (avoids duplicates)

        for label1 in self.single_rotations.keys():
            for label2 in self.single_rotations.keys():
                # Create a frozen set of the pair of rotation labels
                rotation_pair = frozenset([label1, label2])

                # Get the last word in string (the axis) from each rotation label
                rotation1_axis = label1.split(' ')[-1] 
                rotation2_axis = label2.split(' ')[-1]

                # Only consider double rotation if they are on different axes and not already considered
                if rotation1_axis != rotation2_axis and rotation_pair not in frozen_double_rotations:
                    frozen_double_rotations.append(rotation_pair)
        
        # Iterate through list of non-repeating double rotations and create a dictionary of lambda functions
        double_rotations = {}
        for rotation_pair in frozen_double_rotations:
            label1, label2 = rotation_pair
            rotation1, rotation2 = self.single_rotations[label1], self.single_rotations[label2]

            double_rotations[f'{label1} + {label2}'] = \
                        lambda x, rot1=rotation1, rot2=rotation2: rot1(rot2(x))
            
        # Sort the dictionary by key
        sorted_double_rotations = {key: double_rotations[key] for key in sorted(double_rotations)}
        return sorted_double_rotations


class Rotater:
    def __init__(self):
        self.scirot_dict = ScipyRotationDict()

    def rotate_voxel(self, voxel: Voxel, rot_label: str) -> BondDict:
        """
        Rotates a single voxel and returns a dictionary containing the rotated 
        directions as keys and the corresponding bond colors as values.
        
        Args:
            voxel (Voxel): The voxel to be rotated.
            rot_label (str): The rotation label to be applied.
            
        Returns:
            bond_dict (BondDict): A dictionary where keys are the rotated directions 
                              and values are tuples of (bond colors, bond types).
        """
        rot = self.scirot_dict.get_rotation(rot_label)
        
        bond_dict = BondDict()
        for direction, bond in voxel.bond_dict.dict.items():
            # Rotate the direction vector of the bond
            direction = np.array(direction)
            rotated_direction = rot(direction)
            rotated_direction = tuple(np.round(rotated_direction).astype(int)) # format it as a tuple

            # Store the color in the bond_dict with the rotated direction as the key
            rotated_bond = Bond(
                direction=rotated_direction,
                voxel=voxel,
                color=bond.color,
                type=bond.type,
                bond_partner=bond.bond_partner
            )
            bond_dict.dict[rotated_direction] = rotated_bond
        
        return bond_dict

