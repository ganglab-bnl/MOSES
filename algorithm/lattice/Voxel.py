import numpy as np
import logging
from algorithm.lattice.Bond import BondDict, Bond

class Voxel:
    """
    The 'Voxel' represents the octahedral DNA origami, to be tiled in
    the 3D Lattice structure. It contains a material cargo (int) and 
    6 Bonds attached to each vertex. 

    Methods:
        - get_bond(direction): Get the bond in a given direction
        - get_partner(direction): Returns partner Bond + Voxel objects 
                                  in the supplied direction
    """
    def __init__(self, id: int, material: int, coordinates: tuple[float, float, float],
                 np_index: tuple[int, int, int], type=None):
        """
        Initialize a Voxel object with a unique ID, material, and coordinates.
        Args:
            id: the unique identifier for the Voxel
            material: the material cargo of the Voxel
            coordinates: the Voxel's coordinates in the Lattice.MinDesign
            np_index: The 'material' value's index into the MinDesign np.array
            type: Either "structural" or "complementary" based on Painter output
        """
        self.id = id
        self.material = material
        self.coordinates = coordinates
        self.np_index = np_index
        self.type = type

        # ----- Vertex information ----- #
        # Vertex positions for octahedral structures
        self.vertex_names = [
            "+x", "-x", 
            "+y", "-y", 
            "+z", "-z"
        ]
        # Vector (euclidean) representing direction of each vertex 
        # wrt. the Voxel @ (0,0,0)
        self.vertex_directions = [
            (1, 0, 0), (-1, 0, 0),   # +-x
            (0, 1, 0), (0, -1, 0),   # +-y
            (0, 0, 1), (0, 0, -1)    # +-z
        ]

        # Initialize bonds with default values
        self.bond_dict = BondDict({
            direction: Bond(direction=direction, voxel=self) for direction in self.vertex_directions
        })

    
    # --- Public methods --- #
    def get_bond(self, direction) -> Bond:
        """
        Get the bond in a given direction. Accepts '+x', '-y', etc. or 
        a tuple/np.array representing the vector direction of the bond wrt. the
        Voxel @ (0, 0, 0). Wrapper around bond_dict version.
        """
        direction = self._get_direction_tuple(direction)
        return self.bond_dict.get_bond(direction)
    
    def get_partner(self, direction) -> tuple['Voxel', Bond]:
        """
        Get the partner Voxel + Bond objects in the supplied direction.
        (Direction can be str, tuple, or np.ndarray)
        """
        bond = self.get_bond(direction)
        bond_partner = bond.bond_partner

        if bond_partner is None:
            logging.error(f"No bond partner found for Voxel {self.id} in direction {direction}")
            return None, None

        voxel_partner = bond_partner.voxel
        return voxel_partner, bond_partner
    
    def get_all_partner_voxels(self) -> list[int]:
        """Return a list of all ids of voxels we are partners with."""
        partner_voxels = []
        for direction, bond in self.bond_dict.dict.items():
            partner_voxel_id = bond.bond_partner.voxel.id
            partner_voxels.append(partner_voxel_id)
        return partner_voxels

    def get_type(self) -> bool:
        """
        Return the type "structural" or "complementary" of the voxel
        Returns None if not set
        """
        return self.type if self.type else None
    
    def is_fully_colored(self) -> bool:
        """Return whether all bonds on the voxel have a color"""
        count = 0
        for direction, bond in self.bond_dict.dict.items():
            if bond.color is not None or bond.color != 0:
                count += 1
        return True if count==6 else False
    
    def load_bonds(self, bond_dict: BondDict) -> None:
        """
        Loads bonds from another BondDict into the current, only copying
        over the colors/types of the other into the corresponding directions of
        the current BondDict instance.

        Used in map painting procedures.

        Args:
            bond_dict (BondDict): Another BondDict instance whose bond 
                                  color/types will be copied over.
        """
        for direction, bond2 in bond_dict.dict.items():
            bond1 = self.get_bond(direction) # Get Bond on current BondDict

            # Replace color/type attributes with those on the other Bond
            bond1.set_color(bond2.color) 
            bond1.set_type(bond2.type)
    
    def has_bond_partner_with(self, partner_voxel) -> Bond:
        """
        If the voxel has a bond partner with the supplied Voxel object,
        return the current Voxel's bond object which has the partner with the
        partner_voxel.
        
        Args:
            partner_voxel (int or Voxel): The other voxel/voxel_id to check if they are partners
        
        Returns:
            bond (Bond): Bond object on the current voxel which connects it to partner_voxel
        """

        partner_voxel_id = partner_voxel
        if isinstance(partner_voxel, Voxel):
            partner_voxel_id = partner_voxel.id
        
        for bond in self.bond_dict.dict.values():
            if bond.bond_partner is None:
                continue
            if bond.bond_partner.voxel.id == partner_voxel_id:
                return bond
            
        return None
    
    
    def is_palindromic(self, test_color: int) -> bool:
        """
        Check if adding a new bond color will create a palindromic structure.

        Args:
            test_color (int): The color of the new bond we're considering to add
        """
        if test_color is None or test_color == 0:
            return False
        
        for bond in self.bond_dict.dict.values():
            if bond.color == -1*test_color:
                return True
        return False

    def get_bond_type(self, color: int) -> str:
        """
        Get the bond type for all bonds of the given color on the Voxel.
        Args:
            color (int): The color of the bond to search for

        Returns:
            bond_type (str): The bond type of all bonds on the voxel with the 
                             given color (None if not found)
        """
        for bond in self.bonds.values():
            if bond.color == color:
                return bond.type
        return None
    
    def set_type(self, type: str) -> None:
        """
        Set the type of the voxel to "structural" or "complementary"
        """
        self.type = type
    
    def repaint_complement(self, color: int, complement: int) -> None:
        """
        Repaint the bonds of the given color to their complement.
        Args:
            color (int): The abs(color) of the bonds to repaint
        """
        for bond in self.bonds.values():
            if abs(bond.color) == color:
                bond.color = abs(bond.color)*complement
    
    def flip_complementarity(self, color: int, flipped_voxels=None) -> dict[int, int]:
        """
        Flip the complementarity of the bonds with the given color.
        Args:
            color (int): The abs(color) of the bonds to flip
        
        Returns:
            flipped_voxels (dict[int, int]): Dictionary of voxel IDs that would be flipped
                                            and their complementarity multipliers (+1 or -1)
        """
        if flipped_voxels is None:
            flipped_voxels = {}

        # Determine the current complementarity of the voxel
        current_complementarity = self.get_complementarity(color)
        if current_complementarity is None:
            raise ValueError(f"Voxel {self.id} does not have a bond with color {color}")
        
        # If this voxel is already flipped, skip it
        if self.id in flipped_voxels:
            return flipped_voxels

        # Register the flip for the current voxel
        flipped_voxels[self.id] = -current_complementarity  # Flip the complementarity

        for bond in self.bonds.values():
            if abs(bond.color) == color:
                partner_voxel = bond.bond_partner.voxel

                # Recursively flip the partner voxel if it hasn't been flipped already
                if partner_voxel.id not in flipped_voxels:
                    flipped_voxels = partner_voxel.flip_complementarity(color, flipped_voxels)

        return flipped_voxels
    
    def get_complementarity(self, color: int) -> int:
        """
        Get the complementarity of the bonds with the given color.
        Args:
            color (int): The abs(color) of the bonds to check
        Returns:
            complementarity (int): Whether the bond is the color (1) or its complement (-1)
        """
        for bond in self.bonds.values():
            if abs(bond.color) == abs(color):
                complementarity = bond.color // abs(bond.color)
                return complementarity
        
        # Else, means we didn't find bonds of the color on the Voxel
        raise ValueError(f"No bonds of color {color} exist on voxel {self.id}.")


    # Methods written for binding_flexibility calculations
    # -------------------------- #
    def color_dict(self) -> dict[int, list[str]]:
        """
        Get a dictionary of bond colors and their directions.
        """
        color_dict = {}
        for bond in self.bonds.values():
            if bond.color not in color_dict:
                color_dict[bond.color] = []
            color_dict[bond.color].append(self._get_direction_label(bond.direction))
        return color_dict
    
    def most_frequent_color(self) -> int:
        """
        Get the most frequent color of the bonds on the Voxel.
        """
        color_dict = self.color_dict()
        max_color = max(color_dict, key=lambda x: len(color_dict[x]))
        return max_color
    
    def get_partner_voxel(self, direction) -> 'Voxel':
        """
        Get the partner Voxel object in the supplied direction.
        """
        direction = self._get_direction_tuple(direction)
        return self.bonds[direction].bond_partner.voxel
    # -------------------------- #

    # --- Print method --- #
    def print_bonds(self) -> None:
        """Print all bonds of the Voxel."""
        print(f"Voxel {self.id} ({self.material}):\n---")
        for direction, bond in self.bonds.items():
            print(f" -> {self._get_direction_label(direction)}: {bond.color}, {bond.type}")

    # --- Internal methods --- #
    def _get_direction_label(self, direction) -> str:
        """
        Get the label of the direction (ex: '+x', '-y', etc.)
        """
        direction = self._get_direction_tuple(direction)
        direction_index = self.vertex_directions.index(direction)
        return self.vertex_names[direction_index]
        
    def _get_direction_tuple(self, direction):
        """
        Formats any kind of 'direction' input into a tuple.
        Handles:
            - str: "+x", "-y", ...
            - np.array: np.array([1, 0, 0]), ...
            - tuple: (1, 0, 0), ...
        """
        if isinstance(direction, str): 
            # Case 1: direction is a str "+x", "-y", ...
            direction_index = self.vertex_names.index(direction)
            direction = self.vertex_directions[direction_index]

        elif isinstance(direction, np.ndarray): 
            # Case 2: direction is a np.array([1, 0, 0]), ...
            direction = tuple(direction)
        
        return direction # Now direction is a tuple :-)

