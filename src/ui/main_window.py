from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QDockWidget, QPushButton, QToolBar, QLabel, QMessageBox,
    QSplitter, QFileDialog, QMenuBar, QMenu
)
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import QIcon, QAction
import os
from pathlib import Path

from .canvas import VideoCanvas
from .timeline import Timeline
from ..core.video_node import VideoNode

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WeaveClip")
        self.setMinimumSize(1200, 800)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create splitter for canvas and timeline
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Create canvas
        self.canvas = VideoCanvas()
        splitter.addWidget(self.canvas)
        
        # Create timeline
        self.timeline = Timeline()
        splitter.addWidget(self.timeline)
        
        # Set initial splitter sizes
        splitter.setSizes([600, 200])
        
        # Create menu bar
        self.create_menu_bar()
        
        # Set dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QMenuBar {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenuBar::item:selected {
                background-color: #4a9eff;
            }
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #4a4a4a;
            }
            QMenu::item:selected {
                background-color: #4a9eff;
            }
            QDockWidget {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QDockWidget::title {
                background-color: #3a3a3a;
                padding: 5px;
            }
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                border: none;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #5aafff;
            }
            QPushButton:pressed {
                background-color: #3a8eff;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
        # Connect signals
        self.canvas.scene.changed.connect(self.update_timeline)
        
        # Set up node palette
        self.setup_node_palette()
        
        # Load videos from quiver
        self.load_quiver_videos()
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Add video action
        add_video_action = QAction("Add Video", self)
        add_video_action.triggered.connect(self.add_video)
        file_menu.addAction(add_video_action)
        
        # Add refresh quiver action
        refresh_action = QAction("Refresh Quiver", self)
        refresh_action.triggered.connect(self.load_quiver_videos)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def add_video(self):
        """Add a video file to the canvas."""
        try:
            # Open file dialog
            file_dialog = QFileDialog()
            file_dialog.setNameFilter("Video files (*.mp4 *.avi *.mov *.mkv)")
            file_dialog.setViewMode(QFileDialog.ViewMode.List)
            
            if file_dialog.exec():
                # Get selected file
                filenames = file_dialog.selectedFiles()
                if filenames:
                    video_path = filenames[0]
                    
                    # Add video node to canvas
                    pos = self.canvas.mapToScene(
                        self.canvas.viewport().rect().center()
                    )
                    self.canvas.add_video_node(video_path, pos)
                    
                    # Update timeline
                    self.update_timeline()
            
        except Exception as e:
            print(f"Error adding video: {e}")
            QMessageBox.warning(self, "Error", f"Error adding video: {str(e)}")
    
    def update_timeline(self):
        """Update the timeline with current canvas connections."""
        try:
            # Get connections from canvas
            connections = self.canvas.connections
            
            # Update timeline
            self.timeline.update_clips(connections)
            
        except Exception as e:
            print(f"Error updating timeline: {e}")
    
    def setup_node_palette(self):
        """Set up the node palette dock widget."""
        palette_dock = QDockWidget("Node Palette", self)
        palette_dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable |
                               QDockWidget.DockWidgetFeature.DockWidgetFloatable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, palette_dock)
    
    def load_quiver_videos(self):
        """Load all videos from the quiver directory."""
        try:
            # Get quiver directory path
            quiver_dir = Path(__file__).parent.parent.parent / 'quiver'
            if not quiver_dir.exists():
                print(f"Quiver directory not found: {quiver_dir}")
                return
            
            # Find all video files
            video_files = []
            for ext in ['.mp4', '.avi', '.mov', '.mkv']:
                video_files.extend(quiver_dir.glob(f'**/*{ext}'))
            
            if not video_files:
                print("No video files found in quiver directory")
                return
            
            # Clear existing nodes
            self.canvas.scene.clear()
            
            # Add each video as a node
            spacing = 250  # Horizontal spacing between nodes
            x = 50  # Starting x position
            y = 50  # Starting y position
            
            for video_path in video_files:
                # Create node at position
                pos = QPointF(x, y)
                self.canvas.add_video_node(str(video_path), pos)
                
                # Update position for next node
                x += spacing
                
                # Move to next row if too wide
                if x > 800:
                    x = 50
                    y += 300
            
            # Update timeline
            self.update_timeline()
            
        except Exception as e:
            print(f"Error loading quiver videos: {e}")
            QMessageBox.warning(self, "Error", f"Error loading quiver videos: {str(e)}")
    
    def new_project(self):
        """Create a new project."""
        self.canvas.scene.clear()
        self.update_timeline()
