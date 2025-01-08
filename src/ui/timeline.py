from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame,
    QGraphicsView, QGraphicsScene, QGraphicsItem,
    QLabel, QHBoxLayout
)
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QSize
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
import cv2
import numpy as np
import os

class Timeline(QWidget):
    clip_selected = pyqtSignal(str)  # Emitted when a clip is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.clips = []  # List of (node, start_time) tuples
        self.current_time = 0
        self.scale_factor = 100  # pixels per second
        
        # Set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        self.content = TimelineContent()
        scroll.setWidget(self.content)
        
        layout.addWidget(scroll)
        
        # Set dark theme
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QScrollBar:horizontal {
                background: #2a2a2a;
                height: 15px;
            }
            QScrollBar::handle:horizontal {
                background: #4a9eff;
                min-width: 20px;
                border-radius: 7px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
    
    def update_clips(self, connections):
        """Update timeline with connected clips."""
        try:
            # Clear current clips
            self.clips = []
            
            if not connections:
                self.content.update_clips([])
                return
            
            # Process connections to build timeline
            processed_nodes = set()
            
            def process_node(node, start_time):
                """Process a node and its connections recursively."""
                if node in processed_nodes:
                    return
                processed_nodes.add(node)
                
                # Add clip to timeline
                self.clips.append((node, start_time))
                
                # Calculate next start time based on current clip duration
                next_start = start_time + node.duration
                
                # Process next node if it exists
                if node.next_node:
                    process_node(node.next_node, next_start)
            
            # Find root nodes (nodes with no incoming connections)
            root_nodes = set()
            for start_node, end_node in connections:
                # Add all start nodes as potential roots
                root_nodes.add(start_node)
                # Remove any end nodes from roots
                root_nodes.discard(end_node)
            
            # Process each root node
            for root in root_nodes:
                process_node(root, 0)
            
            # Update timeline content
            self.content.update_clips(self.clips)
            
        except Exception as e:
            print(f"Error updating timeline clips: {e}")
            
class TimelineContent(QWidget):
    def __init__(self):
        super().__init__()
        self.clips = []
        self.setMinimumHeight(180)
        self.scale_factor = 100  # pixels per second
        self.setStyleSheet("background-color: #1a1a1a;")
        
    def update_clips(self, clips):
        """Update the list of clips and redraw."""
        self.clips = clips
        total_duration = 0
        for node, start_time in clips:
            clip_end = start_time + node.duration
            total_duration = max(total_duration, clip_end)
        
        # Set widget width based on total duration
        width = max(int(total_duration * self.scale_factor), self.parent().width())
        self.setMinimumWidth(width)
        self.update()
        
    def paintEvent(self, event):
        """Paint the timeline content."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # Draw time markers
            painter.setPen(QPen(QColor("#4a4a4a")))
            total_width = self.width()
            marker_interval = self.scale_factor  # 1 second intervals
            
            for x in range(0, total_width, marker_interval):
                painter.drawLine(x, 0, x, 10)
                time = x / self.scale_factor
                painter.drawText(x - 15, 25, f"{time:.1f}s")
            
            # Draw clips
            clip_height = 100
            y_offset = 40
            
            for node, start_time in self.clips:
                try:
                    # Calculate clip rectangle
                    x = int(start_time * self.scale_factor)
                    width = int(node.duration * self.scale_factor)
                    
                    # Draw clip background
                    painter.setPen(QPen(QColor("#4a9eff")))
                    painter.setBrush(QBrush(QColor("#2a2a2a")))
                    painter.drawRoundedRect(x, y_offset, width, clip_height, 5, 5)
                    
                    # Draw clip name
                    painter.setPen(QPen(Qt.GlobalColor.white))
                    clip_name = os.path.basename(node.video_path)
                    painter.drawText(x + 5, y_offset + 20, clip_name)
                    
                    # Draw duration
                    duration_text = f"{node.duration:.1f}s"
                    painter.drawText(x + 5, y_offset + 40, duration_text)
                    
                except Exception as e:
                    print(f"Error drawing clip: {e}")
            
        except Exception as e:
            print(f"Error painting timeline: {e}")

class TimelineTracks(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Add some sample tracks
        for i in range(5):
            track = TimelineTrack(f"Track {i+1}")
            self.layout.addWidget(track)
        
        self.layout.addStretch()
        self.setMinimumWidth(1000)  # Allow horizontal scrolling

class TimelineTrack(QFrame):
    def __init__(self, name):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("QFrame { background-color: #2a2a2a; }")
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)
        
        # Add track label
        self.label = QLabel(name)
        self.label.setFixedWidth(100)
        self.layout.addWidget(self.label)
        
        # Add track content area
        self.content = TimelineTrackContent()
        self.layout.addWidget(self.content)
        
        self.setFixedHeight(50)

class TimelineTrackContent(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1a1a1a;")
    
    def sizeHint(self):
        return QSize(1000, 40)
