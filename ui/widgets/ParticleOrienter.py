from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QLabel, QPushButton,
    QLineEdit, QComboBox, QAbstractSpinBox
)
from ast import literal_eval

class ParticleOrienter(QWidget):
    orientation_changed = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # a bold font
        self.textbf = QFont()
        self.textbf.setBold(True)

        # title of dimension setter widget
        self.title = QLabel("Set particle orientation")
        self.title.setFont(self.textbf)
        self._layout.addWidget(self.title)

        # important variables
        self.voxels: dict[str, str] = {}
        self.voxels[''] = None

        self.init_voxel_selector()
        self.init_xyz_inputs()

    def init_voxel_selector(self):
        """initialize the UI for selecting a voxel to orient the particle of"""
        # the voxel selector
        # nlays input
        self.select_layout = QHBoxLayout()
        self.select_label = QLabel("voxel: ")
        self.vox_selector = QComboBox()
        self.vox_selector.addItems(
            ["(0,0,0)", "(1,0,0)", "(0,1,0)"]
        )
        self.vox_selector.currentTextChanged.connect(self.trigger_voxel_selected)
        # add the widgets to the layout
        self.select_layout.addWidget(self.select_label)
        self.select_layout.addWidget(self.vox_selector)
        self._layout.addLayout(self.select_layout)

        # the voxel selected (defaults)
        self.voxel_selected = "(0,0,0)"
        self.particle_selected = 0

        self.init_xyz_inputs() # the particle x,y,z inputs

        # submit button
        self.submit_button = QPushButton("Update")
        self.submit_button.clicked.connect(self.trigger_orientation_changed)
        self._layout.addWidget(self.submit_button)

    def init_xyz_inputs(self):
        # the particle position input
        self.pos_label = QLabel(f"particle position ({self.particle_selected}):")
        
        # particle-x input
        self.px_layout = QHBoxLayout()
        self.px_label = QLabel("x: ")
        self.px_input = QDoubleSpinBox()
        self.px_input.setValue(0)
        self.px_input.setRange(-1, 1)
        self.px_input.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        # add the widgets to the layout
        self.px_layout.addWidget(self.px_label)
        self.px_layout.addWidget(self.px_input)
        self.px_layout.addStretch()

        # particle-y input
        self.py_layout = QHBoxLayout()
        self.py_label = QLabel("y: ")
        self.py_input = QDoubleSpinBox()
        self.py_input.setValue(0)
        self.py_input.setRange(-1, 1)
        self.py_input.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        # add the widgets to the layout
        self.py_layout.addWidget(self.py_label)
        self.py_layout.addWidget(self.py_input)
        self.py_layout.addStretch()

        # particle-z input
        self.pz_layout = QHBoxLayout()
        self.pz_label = QLabel("z: ")
        self.pz_input = QDoubleSpinBox()
        self.pz_input.setValue(0)
        self.pz_input.setRange(-1, 1)
        self.pz_input.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        # add the widgets to the layout
        self.pz_layout.addWidget(self.pz_label)
        self.pz_layout.addWidget(self.pz_input)
        self.pz_layout.addStretch()
        
        self._layout.addWidget(self.pos_label)
        self._layout.addLayout(self.px_layout)
        self._layout.addLayout(self.py_layout)
        self._layout.addLayout(self.pz_layout)

    def trigger_voxel_selected(self, text):
        self.voxel_selected = text
        self.particle_selected = self.voxels.get(text)
        self.pos_label.setText(f"particle position ({self.particle_selected}):")

    def trigger_orientation_changed(self):
        voxel_coords = self.voxel_selected
        particle_pos = (self.px_input.value(), self.py_input.value(), self.pz_input.value())

        self.orientation_changed.emit((literal_eval(voxel_coords), particle_pos))
        print(f"voxel {voxel_coords} updated to have particle ({self.particle_selected}) position {particle_pos}")

    def update_voxels(self, grid_cells: dict[tuple, QLineEdit]):
        self.vox_selector.clear()
        self.vox_selector.addItems([str(k) for k in grid_cells.keys()])

        self.voxels = {}
        self.voxels[''] = None
        for v_coords, grid_cell in grid_cells.items():
            self.voxels[str(v_coords)] = grid_cell.text()