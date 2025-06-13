import pyqtgraph.opengl as gl
import numpy as np
from algorithm.lattice.Voxel import Voxel
from ui.visual.ColorDict import ColorDict

class Octa(gl.GLGraphItem):
    def __init__(self, voxel: Voxel, color_dict: ColorDict, spacing=1):
        """give it a voxel which has a center + cargo position / color"""
        super().__init__()
        self._view = None # will be initialized later on plot()
        self.SCALE = 1+spacing
        self.voxel = voxel
        self.cargo_color = color_dict.get_color(self.voxel.cargo)
        self.wireframe_color = color_dict.get_color(0)

        # geometry variables
        self.vertices = [
            (0.5, 0, 0), (-0.5, 0, 0),   # +-x
            (0, 0.5, 0), (0, -0.5, 0),   # +-y
            (0, 0, 0.5), (0, 0, -0.5)    # +-z
        ]
        # each edge tuple holds the two vertices (by indices) they connect
        self.edges = [
            (0, 2), (0, 3), (0, 4), (0, 5),
            (1, 2), (1, 3), (1, 4), (1, 5),
            (2, 4), (2, 5), (3, 4), (3, 5)
        ]
        self.init_geometry()

    def init_geometry(self):
        # initialize the wireframe
        self.lines = []
        for v0, v1 in self.edges:
            line = np.array([self.vertices[v0], self.vertices[v1]]) + (np.array(self.voxel.coords)*self.SCALE)
            line_item = gl.GLLinePlotItem(
                pos=line, 
                color=(0.4, 0.4, 0.4, 1), 
                width=5, 
                antialias=True
            )
            self.lines.append(line_item)

        # initialize the cargo, oriented in space
        particle_mesh = gl.MeshData.sphere(rows=5, cols=5, radius=0.10)
        self.particle = gl.GLMeshItem(
            meshdata=particle_mesh, 
            smooth=True,
            color=self.cargo_color,
            drawEdges=False
        )
        dx = (self.voxel.coords[0]*self.SCALE) + self.voxel.cargo_coords[0]
        dy = (self.voxel.coords[1]*self.SCALE) + self.voxel.cargo_coords[1]
        dz = (self.voxel.coords[2]*self.SCALE) + self.voxel.cargo_coords[2]
        self.particle.translate(dx, dy, dz)
    
    def plot(self, view: gl.GLViewWidget):
        """given a view, plots our octa on the view"""
        self._view = view
        for line in self.lines:
            view.addItem(line)
        view.addItem(self.particle)

    def cleanup(self):
        """Remove all graphical items from their parent view to allow proper cleanup."""
        # remove lines from their parent view if they have one
        if not self._view:
            return
        
        for line in self.lines:
            self._view.removeItem(line)
        self._view.removeItem(self.particle)

        self.lines.clear()
        self.particle = None
        self._view = None