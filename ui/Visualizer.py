from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph.opengl as gl

from ui.visual.Octa import Octa
from ui.visual.Bond import Bond as VisBond
from ui.visual.ColorDict import ColorDict
from algorithm.lattice.Lattice import Lattice
# from algorithm.lattice.Voxel import Voxel
import gc


class Visualizer(QWidget):
    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # the 3d view widget
        self.view = gl.GLViewWidget()
        self.view.setCameraPosition(distance=30)
        self._layout.addWidget(self.view)

        self.view.setBackgroundColor(QColor("#efefef"))
        self.color_dict = ColorDict()
        self.octa_items: list[Octa] = []
        self.bond_items: list[VisBond] = []

    def plot_lattice(self, lattice: Lattice, view_unit_cell=True):
        """plot our given lattice structure"""
        self.cleanup()
        voxels = lattice.voxels if not view_unit_cell else lattice.voxels + lattice.unit_cell_voxels
        self.plot_voxels(voxels)

    def plot_voxels(self, voxels: list['Voxel']):
        """plot only the given list of voxels"""
        self.cleanup()
        for v in voxels:
            # plot the octa
            octa_item = Octa(v, self.color_dict)
            octa_item.plot(self.view)
            self.octa_items.append(octa_item)

            # also plot the bonds
            for b in v.bonds.values():
                bond_item = VisBond(b, self.color_dict)
                bond_item.plot(self.view)
                self.bond_items.append(bond_item)

    def cleanup(self):
        """
        removes items from view and clears the items list 
        (hopefully preventing jupyter kernel crash on rerun)
        """
        for octa_item in self.octa_items:
            octa_item.cleanup()
        for bond_item in self.bond_items:
            bond_item.cleanup()
        gc.collect()

class RunVisualizer:
    def __init__(self, voxels: list['Voxel']=None, lattice: Lattice=None, view_unit_cell=True, app=None):
        import sys
        from PyQt6.QtWidgets import QApplication, QMainWindow

        if app is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = app

        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("Lattice Visualizer")
        self.main_window.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.main_window.setCentralWidget(self.central_widget)

        # initialize the visualizer widget adding it to the layout
        self.vis = Visualizer()
        self.central_layout.addWidget(self.vis)
        self.init_toolbar()

        if voxels is not None:
            self.vis.plot_voxels(voxels)
        elif lattice is not None:
            self.vis.plot_lattice(lattice, view_unit_cell)

        self.main_window.show()
        self.app.exec()

    def init_toolbar(self):
        from PyQt6.QtWidgets import QToolBar
        from PyQt6.QtCore import Qt

        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.addAction("Exit", self.close)
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def close(self):
        self.vis.cleanup()
        self.app.quit()