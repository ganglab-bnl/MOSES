from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QLineEdit, QCheckBox
)

from ui.widgets.DimensionSetter import DimensionSetter
from ui.widgets.LatticeFiller import LatticeFiller
from ui.widgets.ParticleOrienter import ParticleOrienter

from algorithm.lattice.Voxel import Voxel

class Designer(QWidget):

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # split the tab into lattice dimensions / filling
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self._layout.addWidget(self.splitter)

        self.init_lattice_settings()
        self.init_lattice_filler()

        # important variables
        self.voxels = self.particle_orienter.voxels

    def init_lattice_settings(self):
        # --- LEFT SIDE: LATTICE SETTINGS ---
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_panel.setLayout(self.left_layout)

        # create + add dimension setter
        self.dimension_setter = DimensionSetter()
        self.left_layout.addWidget(self.dimension_setter)
        self.dimension_setter.dimensions_changed.connect(self.update_lattice_filler)

        self.particle_orienter = ParticleOrienter()
        self.particle_orienter.orientation_changed.connect(self.update_particle_orientation)
        self.left_layout.addWidget(self.particle_orienter)

         # is unit cell? input
        self.is_unit_cell_layout = QHBoxLayout()
        self.is_unit_cell_label = QLabel("is unit cell? ")
        self.is_unit_cell_input = QCheckBox()
        self.is_unit_cell_input.setChecked(True)
        # add the widgets to the layout
        self.is_unit_cell_layout.addWidget(self.is_unit_cell_label)
        self.is_unit_cell_layout.addWidget(self.is_unit_cell_input)
        self.left_layout.addLayout(self.is_unit_cell_layout)

        self.left_layout.addStretch()

    def init_lattice_filler(self):
        # --- RIGHT SIDE: FILL LATTICE ---
        self.right_panel = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_panel.setLayout(self.right_layout)

        # create + add lattice filler
        self.lattice_filler = LatticeFiller()
        self.lattice_filler.grid_changed.connect(self.update_voxels)
        self.lattice_filler.grid_saved.connect(self.save_voxels)
        self.update_voxels(self.lattice_filler.grid_cells)
        self.right_layout.addWidget(self.lattice_filler)

        self.splitter.addWidget(self.left_panel)
        self.splitter.addWidget(self.right_panel)
        self.splitter.setSizes([200, 700])

    def update_lattice_filler(self, dimensions: tuple[int, int, int]):
        self.lattice_filler.update_grid(dimensions[0], dimensions[1], dimensions[2])
        print(f"changed assembly dimensions to: {dimensions}")

    def update_voxels(self, grid_cells: dict[tuple, QLineEdit]):
        """take the new grid cell orientation and update the shit in particle orienter"""
        self.particle_orienter.update_voxels(grid_cells)

    def save_voxels(self, voxels: list[Voxel]):
        self.voxels = voxels

    def update_particle_orientation(self, new_data: tuple):
        """where new data is a tuple consisting of the voxel coords and the new orientation"""
        print(f"received new data {new_data}")
        v_coords, cargo_coords = new_data
        self.lattice_filler.grid_cargo[v_coords] = cargo_coords

class RunDesigner:
    def __init__(self, app=None):
        import sys
        from PyQt6.QtWidgets import QApplication, QMainWindow

        if app is None:
            self.app = QApplication(sys.argv)
        else:
            self.app = app

        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("Lattice Designer")
        self.main_window.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.main_window.setCentralWidget(self.central_widget)

        # initialize the visualizer widget adding it to the layout
        self.designer = Designer()
        self.central_layout.addWidget(self.designer)
        self.init_toolbar()
        self.designer.lattice_filler.grid_saved.connect(self.close)

    def run(self):
        self.main_window.show()
        self.app.exec()
        return self.designer.voxels

    def init_toolbar(self):
        from PyQt6.QtWidgets import QToolBar
        from PyQt6.QtCore import Qt

        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.addAction("Exit", self.close)
        self.main_window.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def close(self):
        self.app.quit()