from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QTabWidget

from .design.Designer import Designer
from .visualize.Visualizer import Visualizer
from .widgets.MenuBar import MenuBar
from .widgets.StatusBar import StatusBar
from .widgets.ToolBar import ToolBar
from .config import AppConfig

class LatticeDesignerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(AppConfig.APP_NAME)
        self.setGeometry(100, 100, 800, 600)

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Create and configure the QTabWidget
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs, stretch=1)  # Ensure it expands to fill space

        # Initialize design and visualize tabs
        self.Designer = Designer()
        self.tabs.addTab(self.Designer, "Design")

        self.Visualizer = Visualizer()
        self.tabs.addTab(self.Visualizer, "Visualize")

        # Toolbars
        self.create_toolbars()

        # Menu and status bar
        self.setMenuBar(MenuBar(self))
        self.setStatusBar(StatusBar(self))
        
        # Connect the currentChanged signal
        self.tabs.currentChanged.connect(self.update_status_bar)
        self.Designer.latticeSaved.connect(self.Visualizer.create_lattice)
    
    def create_toolbars(self):
        # Top Toolbar
        self.topbar = ToolBar(self, orientation=Qt.Orientation.Horizontal,
                              style=Qt.ToolButtonStyle.ToolButtonTextUnderIcon, icon_size=(24, 24))
        self.topbar.add_button("Open", "resources/icons/windows/imageres-10.ico", self.open_file)
        self.topbar.add_button("Save", "resources/icons/windows/shell32-259.ico", self.save_file)
        self.topbar.add_separator()
        self.topbar.add_button("Exit", "resources/icons/windows/shell32-220.ico", self.exit_app)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.topbar)

        # Right Toolbar
        self.rightbar = ToolBar(self, orientation=Qt.Orientation.Vertical,
                                style=Qt.ToolButtonStyle.ToolButtonIconOnly, icon_size=(24, 24))
        self.rightbar.add_button("Settings", "resources/icons/windows/shell32-315.ico", self.settings_window)
        self.rightbar.add_button("Help", "resources/icons/windows/shell32-167.ico", self.help_window)
        self.addToolBar(Qt.ToolBarArea.RightToolBarArea, self.rightbar)

    def update_status_bar(self):
        # Get the current tab widget
        current_tab = self.tabs.currentWidget()
        # Update the status bar with the current tab's name
        if hasattr(current_tab, 'status_message'):
            # Update the status bar with the custom message
            self.statusBar().showMessage(current_tab.status_message())
        else:
            # Fallback message or action
            self.statusBar().showMessage("Ready")

    def open_file(self):
        print("Open file")

    def save_file(self):
        print("Save file")

    def exit_app(self):
        self.close()

    def settings_window(self):
        print("Settings window")

    def help_window(self):
        print("Help window")