import pyqtgraph.opengl as gl
import numpy as np
from algorithm.lattice.Voxel import Bond as AlgoBond
from ui.visual.ColorDict import ColorDict

class Bond(gl.GLGraphItem):
    def __init__(self, bond: AlgoBond, color_dict: ColorDict, length: int=0.4):
        """give it a voxel which has a center + cargo position / color"""
        super().__init__()
        self._view = None # will be initialized later on plot()
        self.bond = bond
        self.bond_color = self.bond.color if self.bond.color else 0
        self.color = color_dict.get_color(abs(self.bond_color))

        # geometry variables
        self.SCALE: float = 2.0 # from VOXEL
        self.OCTA_RADIUS = 0.25
        self.RADIUS = 0.07
        self.SHAFT_LENGTH = length
        self.TIP_LENGTH = length * 0.38

        self.rot_dict = {
            (0.5, 0, 0): (90, 0, 1, 0),   # +x
            (-0.5, 0, 0): (-90, 0, 1, 0), # -x
            (0, 0.5, 0): (-90, 1, 0, 0),  # +y
            (0, -0.5, 0): (90, 1, 0, 0),  # -y
            (0, 0, 0.5): (0, 0, 0, 1),    # +z
            (0, 0, -0.5): (180, 0, 1, 0)  # -z
        }
        lil = self.TIP_LENGTH if self.bond_color < 0 else 0
        self.tip_trans = {
            (0.5, 0, 0): (self.OCTA_RADIUS+self.SHAFT_LENGTH+lil, 0, 0),   # +x
            (-0.5, 0, 0): (-self.OCTA_RADIUS-(self.SHAFT_LENGTH+lil), 0, 0), # -x
            (0, 0.5, 0): (0, self.OCTA_RADIUS+self.SHAFT_LENGTH+lil, 0),   # +y
            (0, -0.5, 0): (0, -self.OCTA_RADIUS-(self.SHAFT_LENGTH+lil), 0), # -y
            (0, 0, 0.5): (0, 0, self.OCTA_RADIUS+self.SHAFT_LENGTH+lil),   # +z
            (0, 0, -0.5): (0, 0, -self.OCTA_RADIUS-(self.SHAFT_LENGTH+lil))  # -z
        }
        
        self.init_geometry()
        self.translate()

    def init_geometry(self):
        # initialize the SHAFT
        start = (np.array(self.bond.voxel.coords, dtype=float)*self.SCALE) + np.array(self.bond.vertex)
        end = start + (np.array(self.bond.vertex)*self.SHAFT_LENGTH)

        self.shaft = gl.GLLinePlotItem(
            pos=np.array([start, end]),
            color=self.color,
            width=5,
            antialias=True
        )
        # initialize the TIP
        tip_mesh = gl.MeshData.cylinder(
            rows=2, cols=5,
            radius=[self.RADIUS*1.5, 0], length=self.TIP_LENGTH
        )
        self.tip = gl.GLMeshItem(
            meshdata=tip_mesh,
            smooth=True,
            color=self.color,
            drawEdges=False
        )

    def translate(self):
        # TRANSLATE THE TIP
        dx, dy, dz = (coord*self.SCALE for coord in self.bond.voxel.coords) 
        tip_dir = tuple(-np.array(self.bond.vertex)) if self.bond_color < 0 else self.bond.vertex
        self.tip.rotate(*self.rot_dict[tip_dir])

        self.tip.translate(
            dx + self.tip_trans[self.bond.vertex][0],
            dy + self.tip_trans[self.bond.vertex][1],
            dz + self.tip_trans[self.bond.vertex][2]
        )
    
    def plot(self, view: gl.GLViewWidget):
        """given a view, plots our octa on the view"""
        self._view = view
        view.addItem(self.shaft)
        view.addItem(self.tip)

    def cleanup(self):
        """Remove all graphical items from their parent view to allow proper cleanup."""
        # remove lines from their parent view if they have one
        if not self._view:
            return
        
        self._view.removeItem(self.shaft)
        self._view.removeItem(self.tip)

        self.shaft, self.tip = None, None
        self._view = None