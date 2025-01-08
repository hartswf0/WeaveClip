from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPathItem
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPen, QColor, QPainterPath, QPainter

from .widgets.video_node_widget import VideoNodeWidget
from ..core.video_node import VideoNode

class ConnectionItem(QGraphicsPathItem):
    """A graphics item representing a connection between nodes."""
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(QColor("#4a9eff"), 2))
        self.setZValue(-1)  # Put connections behind nodes
        
        # Connect to node movement signals
        self.start_node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        self.end_node.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
        
        # Update path
        self.update_path()
    
    def update_path(self):
        """Update the connection path."""
        try:
            if not self.scene() or not self.start_node.scene() or not self.end_node.scene():
                return
            
            start_pos = self.start_node.output_port_pos() + self.start_node.pos()
            end_pos = self.end_node.input_port_pos() + self.end_node.pos()
            
            # Calculate control points for a smooth curve
            path = QPainterPath()
            path.moveTo(start_pos)
            
            # Calculate control points
            dx = end_pos.x() - start_pos.x()
            dy = end_pos.y() - start_pos.y()
            
            # Adjust control points based on distance
            ctrl_point_offset = min(abs(dx) * 0.5, 200)  # Cap the offset
            
            # Create smooth curve
            control1 = QPointF(start_pos.x() + ctrl_point_offset, start_pos.y())
            control2 = QPointF(end_pos.x() - ctrl_point_offset, end_pos.y())
            
            path.cubicTo(control1, control2, end_pos)
            self.setPath(path)
            
        except Exception as e:
            print(f"Error updating connection path: {e}")
    
    def remove(self):
        """Safely remove the connection."""
        if self.scene():
            self.scene().removeItem(self)

class VideoCanvas(QGraphicsView):
    def __init__(self):
        super().__init__()
        
        # Create scene
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Set up view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        
        # Initialize connection variables
        self.temp_connection = None
        self.start_port = None
        self.start_node = None
        self.connections = []  # List of ConnectionItem objects
        
        # Set dark theme
        self.setStyleSheet("""
            QGraphicsView {
                background-color: #1a1a1a;
                border: none;
            }
        """)
        
        # Connect scene change signal
        self.scene.changed.connect(self.update_connections)
    
    def update_connections(self):
        """Update all connections when the scene changes."""
        try:
            # Verify all connections are still valid
            valid_connections = []
            for conn in self.connections:
                if (conn.start_node.scene() == self.scene and 
                    conn.end_node.scene() == self.scene):
                    conn.update_path()
                    valid_connections.append(conn)
                else:
                    # Clear node references before removing
                    if hasattr(conn.start_node, 'video_node'):
                        conn.start_node.video_node.next_node = None
                    if hasattr(conn.end_node, 'video_node'):
                        conn.end_node.video_node.prev_node = None
                    self.scene.removeItem(conn)
            
            self.connections = valid_connections
            self.update_timeline()
            
        except Exception as e:
            print(f"Error updating connections: {e}")
    
    def add_video_node(self, video_path, pos=None):
        """Add a new video node to the canvas."""
        try:
            # Create video node
            video_node = VideoNode(video_path)
            node_widget = VideoNodeWidget(video_node)
            
            # Set position
            if pos is None:
                pos = self.mapToScene(self.viewport().rect().center())
            node_widget.setPos(pos)
            
            # Add to scene
            self.scene.addItem(node_widget)
            
            # Connect to position changes
            node_widget.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges)
            
            return node_widget
            
        except Exception as e:
            print(f"Error adding video node: {e}")
            return None
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                # Get item under cursor
                pos = self.mapToScene(event.pos())
                items = self.scene.items(pos)
                
                for item in items:
                    if isinstance(item, VideoNodeWidget):
                        # Check if clicking on a port
                        if item.is_over_input_port(pos):
                            self.start_connection(item, 'input', pos)
                            return
                        elif item.is_over_output_port(pos):
                            self.start_connection(item, 'output', pos)
                            return
        
        except Exception as e:
            print(f"Error in mousePressEvent: {e}")
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events."""
        if self.temp_connection:
            pos = self.mapToScene(event.pos())
            self.update_temp_connection(pos)
        
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events."""
        try:
            if event.button() == Qt.MouseButton.LeftButton and self.temp_connection:
                pos = self.mapToScene(event.pos())
                items = self.scene.items(pos)
                
                connection_made = False
                for item in items:
                    if isinstance(item, VideoNodeWidget):
                        if self.start_port == 'output' and item.is_over_input_port(pos):
                            self.finish_connection(item)
                            connection_made = True
                            break
                        elif self.start_port == 'input' and item.is_over_output_port(pos):
                            self.finish_connection(item)
                            connection_made = True
                            break
            
                # Clean up temporary connection
                if self.temp_connection:
                    self.scene.removeItem(self.temp_connection)
                    self.temp_connection = None
            
                # Reset connection state
                self.start_node = None
                self.start_port = None
            
                # Update timeline if connection was made
                if connection_made:
                    self.update_timeline()
        
        except Exception as e:
            print(f"Error in mouseReleaseEvent: {e}")
        
        super().mouseReleaseEvent(event)
    
    def start_connection(self, node, port_type, pos):
        """Start drawing a connection from a port."""
        self.start_node = node
        self.start_port = port_type
        
        # Create temporary connection line
        path = QPainterPath()
        if port_type == 'output':
            path.moveTo(node.output_port_pos() + node.pos())
        else:
            path.moveTo(node.input_port_pos() + node.pos())
        path.lineTo(pos)
        
        self.temp_connection = self.scene.addPath(path, QPen(QColor("#4a9eff"), 2))
    
    def update_temp_connection(self, pos):
        """Update the temporary connection line."""
        if not self.temp_connection:
            return
        
        try:
            # Create new path
            path = QPainterPath()
            if self.start_port == 'output':
                start_pos = self.start_node.output_port_pos() + self.start_node.pos()
            else:
                start_pos = self.start_node.input_port_pos() + self.start_node.pos()
            
            # Calculate control points for curve
            dx = pos.x() - start_pos.x()
            ctrl_point_offset = min(abs(dx) * 0.5, 200)
            
            control1 = QPointF(start_pos.x() + ctrl_point_offset, start_pos.y())
            control2 = QPointF(pos.x() - ctrl_point_offset, pos.y())
            
            path.moveTo(start_pos)
            path.cubicTo(control1, control2, pos)
            
            self.temp_connection.setPath(path)
            
        except Exception as e:
            print(f"Error updating temporary connection: {e}")
    
    def finish_connection(self, end_node):
        """Complete the connection between nodes."""
        try:
            if not self.start_node or not end_node:
                return
            
            # Don't connect a node to itself
            if self.start_node == end_node:
                return
            
            # Determine the correct order of nodes based on port types
            if self.start_port == 'output':
                source_node = self.start_node
                target_node = end_node
            else:
                source_node = end_node
                target_node = self.start_node
            
            # Remove any existing connections to the target node's input
            self.remove_existing_connections(target_node)
            
            # Create new connection
            connection = ConnectionItem(source_node, target_node)
            self.scene.addItem(connection)
            self.connections.append(connection)
            
            # Update the video node connections
            source_node.video_node.next_node = target_node.video_node
            target_node.video_node.prev_node = source_node.video_node
            
            # Clear temporary connection
            if self.temp_connection:
                self.scene.removeItem(self.temp_connection)
                self.temp_connection = None
            
            self.start_node = None
            self.start_port = None
            
            # Update timeline
            self.scene.changed.emit()
            
        except Exception as e:
            print(f"Error finishing connection: {e}")
    
    def remove_existing_connections(self, node):
        """Remove any existing connections to a node's input port."""
        try:
            connections_to_remove = []
            for conn in self.connections:
                if conn.end_node == node:
                    # Clear the node references
                    conn.start_node.video_node.next_node = None
                    conn.end_node.video_node.prev_node = None
                    connections_to_remove.append(conn)
            
            for conn in connections_to_remove:
                self.scene.removeItem(conn)
                self.connections.remove(conn)
            
        except Exception as e:
            print(f"Error removing connections: {e}")
    
    def get_clips_order(self):
        """Get clips in left-to-right, top-to-bottom order as JSON."""
        try:
            clips = []
            for item in self.scene.items():
                if isinstance(item, VideoNodeWidget):
                    pos = item.pos()
                    clips.append({
                        'path': item.video_node.video_path,
                        'x': pos.x(),
                        'y': pos.y()
                    })
            
            # Sort by Y first (top to bottom), then X (left to right)
            grid_size = 300  # Approximate size of a node with spacing
            sorted_clips = sorted(clips, key=lambda c: (int(c['y'] / grid_size), c['x']))
            
            # Return just the paths in order
            return [clip['path'] for clip in sorted_clips]
            
        except Exception as e:
            print(f"Error getting clips order: {e}")
            return []

    def update_timeline(self):
        """Update the timeline with current connections."""
        try:
            # Get all video nodes
            nodes = []
            for item in self.scene.items():
                if isinstance(item, VideoNodeWidget):
                    nodes.append(item.video_node)
            
            # Sort nodes by their widget positions
            sorted_nodes = []
            node_positions = {}
            
            # Get positions for all nodes
            for item in self.scene.items():
                if isinstance(item, VideoNodeWidget):
                    pos = item.pos()
                    node_positions[item.video_node] = (pos.x(), pos.y())
            
            # Sort nodes by position (top-to-bottom, left-to-right)
            grid_size = 300  # Approximate size of a node with spacing
            sorted_nodes = sorted(nodes, 
                key=lambda n: (int(node_positions[n][1] / grid_size), 
                             node_positions[n][0]) if n in node_positions else (0, 0))
            
            # Create connections based on sorted order
            connections = []
            for i in range(len(sorted_nodes)-1):
                curr_node = sorted_nodes[i]
                next_node = sorted_nodes[i+1]
                connections.append((curr_node, next_node))
                
                # Update node connections
                curr_node.next_node = next_node
                next_node.prev_node = curr_node
            
            # Clear connections for last node
            if sorted_nodes:
                sorted_nodes[-1].next_node = None
                if len(sorted_nodes) > 1:
                    sorted_nodes[0].prev_node = None
            
            # Update timeline with connections
            if self.scene and self.scene.views():
                main_window = self.scene.views()[0].window()
                if hasattr(main_window, 'timeline'):
                    main_window.timeline.update_clips(connections)
                    print(f"Updated timeline with {len(connections)} connections")
        
        except Exception as e:
            print(f"Error updating timeline: {e}")
            import traceback
            traceback.print_exc()
    
    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Zoom factor
            factor = 1.1
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)
