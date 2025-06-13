from scipy.spatial.transform import Rotation as R
import numpy as np

from algorithm.lattice.Voxel import Bond

class RotationDict:
    """
    Class for (scipy) rotations for transforming the vertices based on euclidean 
    coordinate space. For use in BondPainter.
    """

    def __init__(self):
        self.translation = {
            'translation': lambda x: x # identity function
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
            raise ValueError(f"invalid rotation label: {rot_label}")
        
        return self.all_rotations.get(rot_label)

    def rotate_bonds(self, bonds: dict[tuple[float, float, float], Bond], rotation) -> dict[tuple[float, float, float], Bond]:
        """return a copy of the rotated bonds"""
        rot = self.get_rotation(rotation) if isinstance(rotation, str) else rotation

        rotated_bonds = {}
        for coords, bond in bonds.items():
            rot_coords = rot(np.array(coords))
            rot_coords_tuple = tuple(round(float(c), 6) for c in rot_coords)
            rotated_bonds[rot_coords_tuple] = bond

        return rotated_bonds


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
    