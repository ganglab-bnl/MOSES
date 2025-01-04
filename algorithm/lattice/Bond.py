from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional

@dataclass
class Bond:
    """
    The 'Bond' dataclass represents a bond attached to a particular 
    direction on a Voxel object. The unique information it holds is 
    its bond 'color' and bond type.

    Note: 
    Complementary colors are denoted as a negative version of the original color.
        -> Ex: 2=red, -2=red (complement)
    """
    direction: Tuple[float, float, float]

    # Optional parameters
    voxel: Optional['Voxel'] = None
    color: Optional[int] = None
    type: Optional[str] = None
    bond_partner: Optional['Bond'] = None

    # Setting methods
    def set_color(self, color: int):
        """Set the color of the bond."""
        self.color = color

    def set_bond_partner(self, bond_partner: 'Bond'):
        """Set the Bond object which this bond is connected to."""
        self.bond_partner = bond_partner

    def set_type(self, type: str = None):
        """Set bond type to be either a 'structural' or 'mapped' bond."""
        self.type = type

    # Getting methods
    def get_label(self) -> str:
        """Get a string label for the bond."""
        direction_index = self.voxel.vertex_directions.index(self.direction)
        return self.voxel.vertex_names[direction_index]
    
    def get_partner_voxel(self) -> 'Voxel':
        """Get the Voxel object that this bond is connected to."""
        return self.bond_partner.voxel if self.bond_partner else None


@dataclass
class BondDict:
    """
    BondDict is the class which handles manipulation of all Bonds at once
    for a single Voxel. For use in rotations, relations.

    Corresponds to data required for octahedral voxels.
    """
    dict: Dict[Tuple[float, float, float], Bond] = field(default_factory=dict)

    def get_bond(self, direction: tuple[float, float, float]):
        """
        Gets the bond in the supplied direction
        """
        return self.dict.get(direction)
    
    