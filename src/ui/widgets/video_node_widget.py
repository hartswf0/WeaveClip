from PyQt6.QtWidgets import (
    QGraphicsItem, QWidget, QVBoxLayout, QSlider,
    QPushButton, QHBoxLayout, QGraphicsProxyWidget,
    QLabel, QDoubleSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, QRectF, QPointF, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QImage
import cv2
import numpy as np
import os

class VideoNodeWidget(QGraphicsItem):
    def __init__(self, video_node):
        super().__init__()
        
        self.video_node = video_node
        self.width = 200
        self.height = 250  # Increased height for controls
        self.port_radius = 8
        self.preview_frame = None
        self.is_playing = False
        self.current_frame = 0
        self.error_message = None
        self.playback_speed = 1.0
        self.is_reversed = False
        
        # Enable item movement and selection
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        # Create video controls
        self.controls = VideoControls(self)
        self.controls_proxy = QGraphicsProxyWidget(self)
        self.controls_proxy.setWidget(self.controls)
        self.controls_proxy.setPos(0, self.height - 100)  # Position at bottom
        
        # Set up playback timer
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.next_frame)
        self.update_playback_interval()
        
        # Load preview
        self.load_preview()
    
    def update_playback_interval(self):
        """Update timer interval based on playback speed."""
        base_interval = 33  # ~30 fps
        self.playback_timer.setInterval(int(base_interval / abs(self.playback_speed)))
    
    def set_playback_speed(self, speed):
        """Set the playback speed."""
        self.playback_speed = speed
        self.update_playback_interval()
    
    def toggle_reverse(self, reversed_state):
        """Toggle reverse playback."""
        self.is_reversed = reversed_state
    
    def load_preview(self):
        """Load the first frame as preview."""
        try:
            # Check if file exists
            if not os.path.exists(self.video_node.video_path):
                self.error_message = "File not found"
                return
            
            cap = cv2.VideoCapture(self.video_node.video_path)
            if not cap.isOpened():
                self.error_message = "Could not open video"
                return
            
            ret, frame = cap.read()
            if not ret:
                self.error_message = "Could not read frame"
                return
            
            # Convert frame from BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Scale frame to fit preview area
            preview_height = self.height - 140  # Leave space for title and controls
            preview_width = self.width - 20    # Leave margin
            
            frame_height, frame_width = frame_rgb.shape[:2]
            scale = min(preview_width/frame_width, preview_height/frame_height)
            new_width = int(frame_width * scale)
            new_height = int(frame_height * scale)
            
            frame_scaled = cv2.resize(frame_rgb, (new_width, new_height))
            
            # Convert to QImage
            height, width, channel = frame_scaled.shape
            bytes_per_line = 3 * width
            self.preview_frame = QImage(frame_scaled.data, width, height, 
                                     bytes_per_line, QImage.Format.Format_RGB888).copy()
            
            # Update controls with video duration
            if hasattr(self, 'controls'):
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                self.controls.slider.setMaximum(total_frames - 1)
            
            cap.release()
            
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
            print(f"Error loading preview for {self.video_node.video_path}: {e}")
    
    def next_frame(self):
        """Load and display the next frame during playback."""
        if not self.is_playing:
            return
        
        try:
            cap = cv2.VideoCapture(self.video_node.video_path)
            if not cap.isOpened():
                return
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Update current frame based on direction
            if self.is_reversed:
                self.current_frame -= 1
                if self.current_frame < 0:
                    self.current_frame = total_frames - 1
            else:
                self.current_frame += 1
                if self.current_frame >= total_frames:
                    self.current_frame = 0
            
            # Set position to current frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            
            # Read frame
            ret, frame = cap.read()
            if ret:
                # Convert and scale frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                preview_height = self.height - 140
                preview_width = self.width - 20
                
                frame_height, frame_width = frame_rgb.shape[:2]
                scale = min(preview_width/frame_width, preview_height/frame_height)
                new_width = int(frame_width * scale)
                new_height = int(frame_height * scale)
                
                frame_scaled = cv2.resize(frame_rgb, (new_width, new_height))
                
                # Update preview frame
                height, width, channel = frame_scaled.shape
                bytes_per_line = 3 * width
                self.preview_frame = QImage(frame_scaled.data, width, height,
                                         bytes_per_line, QImage.Format.Format_RGB888).copy()
                
                # Update slider position
                self.controls.slider.setValue(self.current_frame)
                
                # Trigger repaint
                self.update()
            
            cap.release()
            
        except Exception as e:
            print(f"Error during playback: {e}")
    
    def boundingRect(self):
        """Define the bounding rectangle of the widget."""
        return QRectF(0, 0, self.width, self.height)
    
    def input_port_pos(self):
        """Get the position of the input port."""
        return QPointF(self.port_radius, self.height/2)
    
    def output_port_pos(self):
        """Get the position of the output port."""
        return QPointF(self.width - self.port_radius, self.height/2)
    
    def is_over_input_port(self, pos):
        """Check if the given position is over the input port."""
        input_pos = self.mapFromScene(pos)
        port_pos = self.input_port_pos()
        return (input_pos - port_pos).manhattanLength() < self.port_radius * 2
    
    def is_over_output_port(self, pos):
        """Check if the given position is over the output port."""
        output_pos = self.mapFromScene(pos)
        port_pos = self.output_port_pos()
        return (output_pos - port_pos).manhattanLength() < self.port_radius * 2
    
    def paint(self, painter: QPainter, option, widget):
        """Paint the node widget."""
        try:
            # Draw node background
            if self.isSelected():
                painter.setPen(QPen(QColor("#4a9eff"), 2))
            else:
                painter.setPen(QPen(QColor("#4a4a4a"), 2))
            
            painter.setBrush(QBrush(QColor("#2a2a2a")))
            painter.drawRoundedRect(0, 0, self.width, self.height, 10, 10)
            
            # Draw title
            painter.setPen(QPen(Qt.GlobalColor.white))
            title = os.path.basename(self.video_node.video_path)
            painter.drawText(QRectF(10, 5, self.width-20, 20), 
                           Qt.AlignmentFlag.AlignCenter, title)
            
            # Draw preview frame
            if self.preview_frame:
                preview_rect = QRectF(10, 30, self.width-20, self.height-140)
                painter.drawImage(preview_rect, self.preview_frame)
            elif self.error_message:
                painter.drawText(QRectF(10, 30, self.width-20, self.height-140),
                               Qt.AlignmentFlag.AlignCenter, self.error_message)
            
            # Draw ports with better visibility
            # Input port (left)
            input_pos = self.input_port_pos()
            painter.setPen(QPen(QColor("#4a9eff"), 2))
            painter.setBrush(QBrush(QColor("#2a2a2a")))
            painter.drawEllipse(input_pos, self.port_radius, self.port_radius)
            
            # Output port (right)
            output_pos = self.output_port_pos()
            painter.setPen(QPen(QColor("#4a9eff"), 2))
            painter.setBrush(QBrush(QColor("#2a2a2a")))
            painter.drawEllipse(output_pos, self.port_radius, self.port_radius)
            
            # Draw port labels for better clarity
            painter.setPen(QPen(Qt.GlobalColor.white))
            painter.drawText(QRectF(input_pos.x() - 20, input_pos.y() - 20, 
                                  40, 20), Qt.AlignmentFlag.AlignCenter, "In")
            painter.drawText(QRectF(output_pos.x() - 20, output_pos.y() - 20,
                                  40, 20), Qt.AlignmentFlag.AlignCenter, "Out")
            
        except Exception as e:
            print(f"Error painting node: {e}")

class VideoControls(QWidget):
    def __init__(self, parent_node):
        super().__init__()
        self.parent_node = parent_node
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 5)
        
        # Create slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(0)
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)
        
        # Create buttons layout
        button_layout = QHBoxLayout()
        
        # Create play/pause button
        self.play_button = QPushButton("Play")
        self.play_button.setFixedWidth(60)
        self.play_button.clicked.connect(self.toggle_playback)
        button_layout.addWidget(self.play_button)
        
        # Add speed control with better contrast
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Speed:")
        speed_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        speed_layout.addWidget(speed_label)
        
        self.speed_spin = QDoubleSpinBox()
        self.speed_spin.setRange(0.1, 10.0)
        self.speed_spin.setValue(1.0)
        self.speed_spin.setSingleStep(0.1)
        self.speed_spin.setFixedWidth(70)
        self.speed_spin.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_spin)
        
        # Add reverse checkbox with better contrast
        self.reverse_check = QCheckBox("Reverse")
        self.reverse_check.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-weight: bold;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2a2a2a;
                border: 2px solid #4a9eff;
            }
            QCheckBox::indicator:checked {
                background-color: #4a9eff;
                border: 2px solid #4a9eff;
            }
            QCheckBox::indicator:hover {
                border-color: #7ab9ff;
            }
        """)
        self.reverse_check.stateChanged.connect(self.on_reverse_changed)
        speed_layout.addWidget(self.reverse_check)
        
        layout.addLayout(button_layout)
        layout.addLayout(speed_layout)
        
        # Set dark theme with better contrast
        self.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #4a9eff;
                height: 6px;
                background: #2a2a2a;
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4a9eff;
                border: none;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::handle:horizontal:hover {
                background: #7ab9ff;
            }
            QPushButton {
                background-color: #4a9eff;
                color: #ffffff;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7ab9ff;
            }
            QDoubleSpinBox {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 2px solid #4a9eff;
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
            }
            QDoubleSpinBox:hover {
                border-color: #7ab9ff;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background-color: #4a9eff;
                border: none;
                border-radius: 2px;
                margin: 1px;
            }
            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {
                background-color: #7ab9ff;
            }
            QLabel {
                color: #ffffff;
                font-weight: bold;
            }
        """)
    
    def toggle_playback(self):
        """Toggle video playback."""
        if self.parent_node.is_playing:
            self.parent_node.is_playing = False
            self.parent_node.playback_timer.stop()
            self.play_button.setText("Play")
        else:
            self.parent_node.is_playing = True
            self.parent_node.playback_timer.start()
            self.play_button.setText("Pause")
    
    def on_slider_changed(self, value):
        """Handle slider value changes."""
        self.parent_node.current_frame = value
        # Load and display the frame at the new position
        try:
            cap = cv2.VideoCapture(self.parent_node.video_node.video_path)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_POS_FRAMES, value)
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    preview_height = self.parent_node.height - 140
                    preview_width = self.parent_node.width - 20
                    
                    frame_height, frame_width = frame_rgb.shape[:2]
                    scale = min(preview_width/frame_width, preview_height/frame_height)
                    new_width = int(frame_width * scale)
                    new_height = int(frame_height * scale)
                    
                    frame_scaled = cv2.resize(frame_rgb, (new_width, new_height))
                    
                    height, width, channel = frame_scaled.shape
                    bytes_per_line = 3 * width
                    self.parent_node.preview_frame = QImage(
                        frame_scaled.data, width, height,
                        bytes_per_line, QImage.Format.Format_RGB888
                    ).copy()
                    
                    self.parent_node.update()
                
                cap.release()
                
        except Exception as e:
            print(f"Error updating frame: {e}")
    
    def on_speed_changed(self, value):
        """Handle speed changes."""
        self.parent_node.set_playback_speed(value)
    
    def on_reverse_changed(self, state):
        """Handle reverse playback changes."""
        self.parent_node.toggle_reverse(state == Qt.CheckState.Checked.value)
