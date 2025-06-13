from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QGridLayout, QLineEdit
)
from algorithm.lattice.Voxel import Voxel

class LatticeFiller(QWidget):
    grid_changed = pyqtSignal(dict)
    grid_saved = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # a bold font
        self.textbf = QFont()
        self.textbf.setBold(True)

        # title of dimension setter widget
        self.title = QLabel("Fill Lattice")
        self.title.setFont(self.textbf)
        self._layout.addWidget(self.title)

        # the scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.lattice_container = QWidget()
        self.grid_layout = QGridLayout()
        self.lattice_container.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.lattice_container)
        self._layout.addWidget(self.scroll_area)

        # lattice variables
        self.dimensions = (3, 3, 3) # default nlays, nrows, ncols
        self.grid_cells: dict[tuple, QLineEdit] = {} # dict {(vox.coords): grid_cell}
        self.grid_cargo: dict[tuple, tuple] = {} # dict {(abs vox.coords): particle_orientation}
        self.update_grid(3,3,3)

        # create lattice button
        self.create_btn_layout = QHBoxLayout()
        self.create_btn_layout.addStretch()
        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.create_lattice)
        self.create_btn_layout.addWidget(self.create_button)

        self._layout.addLayout(self.create_btn_layout)

    def update_grid(self, nlays: int, nrows: int, ncols: int):
        """update the grid to have nlays, ncols, nrows

        NOTE: our coordinate system is z=reversed(nlays), y=ncols, x=nrows
        """
        self.dimensions = (nlays, nrows, ncols)

        # get rid of old grid cells
        for i in reversed(range(self.grid_layout.count())):
            layout_item = self.grid_layout.itemAt(i)
            widget = layout_item.widget() if layout_item else None
            if widget is not None:
                widget.deleteLater()
        self.grid_cells = {}
        self.grid_cargo = {}

        # create grids
        row_i = 0
        
        for lay in range(nlays):
            # add the layer label
            layer_label = QLabel(f"Layer {lay + 1}")
            self.grid_layout.addWidget(layer_label, row_i, 0, 1, ncols)
            row_i += 1

            for row in range(nrows):
                for col in range(ncols):
                    # create line edit for each cell in lattice
                    cell = QLineEdit()
                    # update outside lattice when grid cells change
                    self.grid_layout.addWidget(cell, row_i, col)

                    # convert to our lattice absolute coordinates
                    z = (nlays-1) - (lay%nlays)
                    y = (nrows-1) - (row%nrows)
                    x = col
                    self.grid_cells[(x,y,z)] = cell # and store for later
                    self.grid_cargo[(x,y,z)] = (0,0,0) # default cargo position
                    cell.textChanged.connect(lambda: self.grid_changed.emit(self.grid_cells))

                row_i += 1

        self.grid_layout.setRowStretch(row_i, 1)
        self.grid_changed.emit(self.grid_cells)

    def create_lattice(self):
        print("create the lattice - parse stored voxel / cargo orientation info and use it to make our thing")
        
        voxels = []
        for v_coords, cargo in self.grid_cells.items():
            cargo_coords = self.grid_cargo[v_coords]
            cargo = int(cargo.text()) if len(cargo.text()) > 0 else 0
            print(f"coords: {v_coords}, cargo: {cargo} @ {cargo_coords}")
            v = Voxel(coords=v_coords, cargo=cargo, cargo_coords=cargo_coords)
            voxels.append(v)
        
        self.grid_saved.emit(voxels)
