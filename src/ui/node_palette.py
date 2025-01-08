from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, 
    QPushButton, QLabel, QFrame, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QIcon, QDrag

class NodePalette(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        
        # Create scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        
        # Add node categories
        self.add_category("Media")
        self.add_category("Transitions")
        self.add_category("Effects")
        self.add_category("Audio")
        
        # Add stretch to push everything to the top
        self.content_layout.addStretch()
        
        # Set up scroll area
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

    def add_category(self, name):
        category = NodeCategory(name)
        self.content_layout.addWidget(category)

class NodeCategory(QFrame):
    def __init__(self, name):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 5px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Add header
        header = QLabel(name)
        header.setStyleSheet("font-weight: bold; color: #ffffff;")
        layout.addWidget(header)
        
        # Add sample nodes based on category
        if name == "Media":
            self.add_node(layout, "Video Clip")
            self.add_node(layout, "Image")
            self.add_node(layout, "Audio File")
        elif name == "Transitions":
            self.add_node(layout, "Cut")
            self.add_node(layout, "Fade")
            self.add_node(layout, "Wipe")
        elif name == "Effects":
            self.add_node(layout, "Color Grade")
            self.add_node(layout, "Speed")
            self.add_node(layout, "Transform")
        elif name == "Audio":
            self.add_node(layout, "Volume")
            self.add_node(layout, "EQ")
            self.add_node(layout, "Fade")
    
    def add_node(self, layout, name):
        node = NodeButton(name)
        layout.addWidget(node)

class NodeButton(QPushButton):
    def __init__(self, name):
        super().__init__(name)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                border: none;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
        """)
        self.setFixedHeight(30)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.text())
            drag.setMimeData(mime_data)
            
            # Start drag operation
            drag.exec(Qt.DropAction.CopyAction)

class NodePaletteList(QListWidget):
    """A palette of available nodes that can be dragged onto the canvas."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setup_nodes()
    
    def setup_nodes(self):
        """Add available node types to the palette."""
        nodes = [
            "Video Clip",
            "Image",  # TODO: Implement image support
            "Text",   # TODO: Implement text support
            "Audio"   # TODO: Implement audio support
        ]
        
        for node in nodes:
            item = QListWidgetItem(node)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsDragEnabled)
            self.addItem(item)
    
    def startDrag(self, supported_actions):
        """Start drag operation with the selected item."""
        item = self.currentItem()
        if item is None:
            return
        
        mime_data = QMimeData()
        mime_data.setText(item.text())
        
        drag = QDrag(self)
        drag.setMimeData(mime_data)
        
        drag.exec(supported_actions)
