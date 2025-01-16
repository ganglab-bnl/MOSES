from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import pyqtSignal
import numpy as np
from .SetDimensions import SetDimensions
from .FillDimensions import FillDimensions
from algorithm.lattice.Lattice import Lattice

class Designer(QWidget):
    latticeSaved = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.mainLayout = QHBoxLayout()
        self.setLayout(self.mainLayout)
        # --------------------- #
        # Shared variables
        # --------------------- #
        self.n_rows = 3
        self.n_columns = 3
        self.n_layers = 3
        self.lattice = np.zeros((self.n_rows, self.n_columns, self.n_layers))

        # --------------------- #
        # Side panel
        # --------------------- #
        self.sidePanelLayout = QVBoxLayout()  # Or QVBoxLayout for vertical arrangement
        self.setDimensionsWidget = SetDimensions()

        # Frame with light grey for visual distinction
        self.sidePanelFrame = QFrame()
        self.sidePanelFrame.setLayout(self.sidePanelLayout)
        self.sidePanelFrame.setFixedWidth(200)  # Set the width of the side panel
        # self.sidePanelFrame.setStyleSheet("background-color: lightgray;")  # Visual distinction

        self.sidePanelLayout.addWidget(self.setDimensionsWidget)
        self.mainLayout.addWidget(self.sidePanelFrame) # Add sidePanel to main layout
        

        # Create a vertical line as a QFrame
        verticalLine = QFrame()
        verticalLine.setFrameShape(QFrame.Shape.VLine) 
        verticalLine.setFrameShadow(QFrame.Shadow.Plain)  
        verticalLine.setStyleSheet("color: lightgray;")  # Set the color of the line
        self.mainLayout.addWidget(verticalLine)

        # --------------------- #
        # Main content
        # --------------------- #
        self.fillDimensionsWidget = FillDimensions(parent=self)
        self.mainLayout.addWidget(self.fillDimensionsWidget)

        # --------------------- #
        # Signal / slot connections
        # --------------------- #
        # Connect the dimensionsChanged signal to a slot method
        self.setDimensionsWidget.dimensionsChanged.connect(self.fillDimensionsWidget.updateGrid)
        self.setDimensionsWidget.clearLatticeClicked.connect(self.fillDimensionsWidget.clearGrid)
        self.setDimensionsWidget.fillZerosClicked.connect(self.fillDimensionsWidget.fillZeros)
        self.setDimensionsWidget.saveLatticeClicked.connect(self.fillDimensionsWidget.saveLattice)
        
        # Initialize fillDimensionsWidget with default values
        self.fillDimensionsWidget.updateGrid(3, 3, 3)

    # Slot method to handle the dimensionsChanged signal
    def updateDimensions(self, rows, columns, layers):
        self.fillDimensionsWidget.updateGrid(rows, columns, layers)

    def setLattice(self, lattice: np.ndarray):
        """
        Save lattice to class attributes and emit the latticeSaved signal
        """
        self.lattice = lattice
        self.latticeSaved.emit(self.lattice)
        print(f'Saved lattice:\n{self.lattice}\n')



class RunDesigner:

    def __init__(self, app=None):
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

        # Initialize Designer and add it to the layout
        self.window = Designer()
        self.mainLayout.addWidget(self.window)
        self.window.latticeSaved.connect(self.lattice_saved)
        self.lattice = None  # Placeholder for the lattice

        # Create and configure the toolbar
        self.toolbar = QToolBar("Main Toolbar", self.mainWindow)
        self.toolbar.setOrientation(Qt.Orientation.Horizontal)
        self.toolbar.addAction("Exit", self.close)
        self.mainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def run(self):
        self.mainWindow.show()
        self.app.exec()
        return self.lattice  # Return the lattice after the app exits

    def lattice_saved(self, lattice):
        self.lattice = lattice  # Store the lattice
        self.app.quit()  # Quit the application

    def close(self):
        self.app.quit()