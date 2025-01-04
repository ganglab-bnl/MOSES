import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtGui import QColor
import numpy as np
import math

from .Voxel import Voxel
from .Bond import Bond
from .ColorDict import ColorDict
from algorithm.lattice.Lattice2 import Lattice

class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Set up the 3D view widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=30)
        self.layout.addWidget(self.view)

        # Colors
        self.colordict = ColorDict(100)

        # Ball / arrow parameters
        self.voxel_radius = 0.5
        self.bond_length = 1.0
        self.voxel_distance = 2.5
        self.directions = [(1, 0, 0), (-1, 0, 0),  # +/- x
                           (0, 1, 0), (0, -1, 0),  # +/- y
                           (0, 0, 1), (0, 0, -1)]  # +/- z
        
        # initialize with default lattice / view
        self.lattice = Lattice(np.zeros((3, 3, 3)))
        self.view_lattice(self.lattice)

        self.view.setBackgroundColor(QColor("#efefef"))
        self.add_axes()

        
    def add_axes(self):
        """Adds 3 arrows indicating x, y, z axes to the view at position -1, -1, -1"""
        axes_directions = [
            np.array([1, 0, 0]), # x
            np.array([0, 1, 0]), # y
            np.array([0, 0, 1]) # z
        ]
        for axis in axes_directions:
            shaft, arrow = Bond.create_bond_old(-3, -3, -3, axis)
            shaft.translate(-1, -1, -1)
            arrow.translate(-1, -1, -1)
            self.view.addItem(shaft)
            self.view.addItem(arrow)


    def adjust_camera_to_fit_lattice(self, x_dim, y_dim, z_dim):
        """
        Uses math to determine how far away to position the camera based on
        the dimensions of voxels we want to visualize

        Args:
            x_dim: how many voxels long in x direction
            y_dim: how many voxels long in y direction
            z_dim: how many voxels long in z direction
        """
        # Compute total length of the lattice in each dimension
        lattice_xlen = (self.voxel_radius*2 + self.voxel_distance) * x_dim
        lattice_ylen = (self.voxel_radius*2 + self.voxel_distance) * y_dim
        lattice_zlen = (self.voxel_radius*2 + self.voxel_distance) * z_dim

        # Calculate the radius of the sphere that encloses the lattice
        # This is the distance from the center of the lattice to a corner
        half_diagonal = math.sqrt(lattice_xlen**2 + lattice_ylen**2 + lattice_zlen**2) / 2
        
        # Assuming a default FOV of 60 degrees for the camera. Adjust as necessary.
        fov_rad = math.radians(60 / 2)  # Half FOV in radians
        distance = half_diagonal / math.sin(fov_rad)  # Calculate the necessary distance
        
        # Set the camera position to ensure the entire lattice is visible
        self.view.setCameraPosition(distance=distance)

    def clear_view(self) -> None:
        """Clears all items from view"""
        self.view.items = []

    def create_lattice(self, input_lattice: np.ndarray) -> Lattice:
        """
        Create a Lattice from a numpy array for use in other parts of the app
        """
        lattice = Lattice(input_lattice)
        return lattice

    def view_voxels(self, voxels: list[Voxel]):
        """
        View all Voxel objects in the list. Uses the Voxel.coordinates to determine where in
        the scene to visualize each object.
        """
        self.clear_view()
        self.add_axes() # re-add axes

        # just initialize view with default distance away (it's fine...)

        # create voxel objects for each voxel in the list
        for voxel in voxels:
            
            # create bond objects attached to each voxel
            for _, bond in voxel.bond_dict.dict.items():
                shaft, arrow = Bond.create_bond(bond)
                self.view.addItem(shaft)
                if arrow is not None: # arrows are not drawn for non-colored bonds
                    self.view.addItem(arrow)

            # create the voxel object
            new_voxel = Voxel.create_voxel(
                x=voxel.coordinates[0]*self.voxel_distance, 
                y=voxel.coordinates[1]*self.voxel_distance, 
                z=voxel.coordinates[2]*self.voxel_distance,
                color=self.colordict.get_color(voxel.material)
            )
            self.view.addItem(new_voxel)


    def view_lattice(self, lattice: Lattice):
        """
        Visualize the current lattice in self.lattice.
        Since lattice.voxels corresponds to only MinDesign voxels, ignores extra layers
        of unit cell. Let's add in unit cell viewing later! :p
        """
        # run the algorithm (not yet - let's refactor this into separate place)
        # lattice.compute_symmetries()
        # self.painter = Painter(lattice)
        # self.painter.paint_lattice()

        self.clear_view() # clear all items
        self.add_axes() # re-add the axes

        n_layers, n_rows, n_columns = lattice.MinDesign.shape
        self.adjust_camera_to_fit_lattice(n_layers, n_rows, n_columns)

        # Call other function to view voxels in mindesign
        #TODO: add separate unit cell viewing
        self.view_voxels(voxels=lattice.voxels.values())

    
    def cleanup_gl_resources(self):
        """Removes items from view and clears the items list 
           (hopefully preventing jupyter kernel crash on rerun)"""
        for item in self.view.items:
            self.view.removeItem(item)

        self.view.items = []
    
class RunVisualizer:
    
    def __init__(self, lattice: Lattice, voxels=None, app=None):
        """Runs the window for a given lattice design"""
        import sys
        from PyQt6.QtWidgets import QApplication, QMainWindow, QToolBar
        from PyQt6.QtCore import Qt
        from ..config import AppConfig

        if app is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = app

        AppConfig.initialize()

        self.mainWindow = QMainWindow()
        self.mainWindow.setWindowTitle("Lattice Visualizer")
        self.mainWindow.setGeometry(100, 100, 800, 600)

        # Create a central widget and set the layout for it
        self.centralWidget = QWidget()
        self.mainLayout = QVBoxLayout(self.centralWidget)
        self.mainWindow.setCentralWidget(self.centralWidget)

        # Initialize VisualizeWindow and add it to the layout
        self.window = Visualizer()
        self.mainLayout.addWidget(self.window)

        # Create and configure the toolbar
        self.toolbar = QToolBar("Main Toolbar", self.mainWindow)
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.addAction("Exit", self.close)
        self.mainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Draw the lattice structure of voxels + bonds
        if voxels is not None:
            # adjust camera to whatever the mindesign is
            n_layers, n_rows, n_columns = lattice.MinDesign.shape
            self.window.adjust_camera_to_fit_lattice(n_layers, n_rows, n_columns)
            self.window.view_voxels(voxels)
        else:
            self.window.view_lattice(lattice)

        self.mainWindow.show()
        self.app.exec()

    def close(self):
        self.window.cleanup_gl_resources()
        self.app.quit()