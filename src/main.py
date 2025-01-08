#!/usr/bin/env python3
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QLibraryInfo, QDir

# Add the project root to Python path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow

def setup_qt_paths():
    """Set up Qt platform plugin paths."""
    # Get Qt library paths from the installation
    qt_plugin_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath)
    if qt_plugin_path and os.path.exists(qt_plugin_path):
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
        print(f"Set QT_QPA_PLATFORM_PLUGIN_PATH to: {qt_plugin_path}")
    else:
        print("Warning: Could not find Qt plugins path")

def main():
    # Set up Qt paths before creating QApplication
    setup_qt_paths()
    
    # Create the application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = MainWindow()
    window.setWindowTitle("WeaveClip")
    window.resize(1200, 800)
    window.show()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
