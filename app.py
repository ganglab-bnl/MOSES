import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget
)

from ui.Designer import Designer
from ui.Visualizer import Visualizer
from algorithm.lattice.Lattice import Lattice
from algorithm.lattice.Voxel import Voxel

class MosesApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # basic window stuff
        self.setWindowTitle("Assembly Designer")
        self.setGeometry(100, 100, 800, 600)

        # central widget for everything
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self._layout = QVBoxLayout(self.central_widget)

        # tab manager
        self.tab_manager = QTabWidget()
        self._layout.addWidget(self.tab_manager)

        # add the tabs
        self.design_tab = Designer()
        self.tab_manager.addTab(self.design_tab, "Design")
        self.design_tab.lattice_filler.grid_saved.connect(self.update_lattice)

        # lattice
        self.lattice = None
        self.visualize_tab = Visualizer()
        # self.visualize_tab.plot_lattice(self.lattice)
        self.tab_manager.addTab(self.visualize_tab, "Visualize")


    def update_lattice(self, voxels: list[Voxel]):
        is_unit_cell = self.design_tab.is_unit_cell_input.isChecked()
        self.lattice = Lattice(voxels, is_unit_cell)
        self.visualize_tab.plot_lattice(self.lattice, is_unit_cell)


if __name__=="__main__":
    # create the pyqt application instance and run it
    app = QApplication(sys.argv)
    main_window = MosesApp()
    main_window.show()
    sys.exit(app.exec())