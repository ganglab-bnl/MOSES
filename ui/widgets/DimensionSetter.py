from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDoubleSpinBox, QLabel, QPushButton
)

class DimensionSetter(QWidget):

    dimensions_changed = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        # a bold font
        self.textbf = QFont()
        self.textbf.setBold(True)

        # title of dimension setter widget
        self.title = QLabel("Set dimensions")
        self.title.setFont(self.textbf)
        self._layout.addWidget(self.title)

        # nlays input
        self.nlays_layout = QHBoxLayout()
        self.nlays_label = QLabel("# lays: ")
        self.nlays_input = QDoubleSpinBox()
        self.nlays_input.setValue(3)
        # add the widgets to the layout
        self.nlays_layout.addWidget(self.nlays_label)
        self.nlays_layout.addWidget(self.nlays_input)

        # nrows inputs
        self.nrows_layout = QHBoxLayout()
        self.nrows_label = QLabel("# rows: ")
        self.nrows_input = QDoubleSpinBox()
        self.nrows_input.setValue(3) # default nrows
        # add the widgets to the layout
        self.nrows_layout.addWidget(self.nrows_label)
        self.nrows_layout.addWidget(self.nrows_input)

        # ncols input
        self.ncols_layout = QHBoxLayout()
        self.ncols_label = QLabel("# cols: ")
        self.ncols_input = QDoubleSpinBox()
        self.ncols_input.setValue(3)
        # add the widgets to the layout
        self.ncols_layout.addWidget(self.ncols_label)
        self.ncols_layout.addWidget(self.ncols_input)

        # add the different layouts to the setter
        self._layout.addLayout(self.nlays_layout)
        self._layout.addLayout(self.nrows_layout)
        self._layout.addLayout(self.ncols_layout)

        # submit button
        self.submit_button = QPushButton("Update")
        self.submit_button.clicked.connect(self.trigger_dimensions_changed)
        self._layout.addWidget(self.submit_button)
        
    def trigger_dimensions_changed(self):
        """trigger dimensions_changed signal"""
        #TODO: input validation
        nlays = int(self.nlays_input.value())
        nrows = int(self.nrows_input.value())
        ncols = int(self.ncols_input.value())

        new_dimensions = (nlays, nrows, ncols)
        self.dimensions_changed.emit(new_dimensions)