import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.ui.main_window import MainWindow

class TestGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Create the application."""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """Create a fresh window before each test."""
        self.window = MainWindow()
    
    def tearDown(self):
        """Clean up after each test."""
        self.window.close()
        del self.window
    
    def test_window_creation(self):
        """Test that the window has the correct title"""
        self.assertIn("WeaveClip", self.window.windowTitle())
    
    def test_canvas_exists(self):
        """Test that canvas is created"""
        self.assertIsNotNone(self.window.canvas)
    
    def test_timeline_exists(self):
        """Test that timeline is created"""
        self.assertIsNotNone(self.window.timeline)

if __name__ == '__main__':
    unittest.main()
