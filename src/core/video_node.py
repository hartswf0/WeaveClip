import uuid
from pathlib import Path
import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
import ffmpeg
import os
import logging

class VideoNode(QObject):
    """A node that represents a video clip with various operations and effects."""
    
    # Signals for node state changes
    state_changed = pyqtSignal()
    preview_updated = pyqtSignal(np.ndarray)
    
    def __init__(self, video_path: str = None):
        super().__init__()
        self.id = str(uuid.uuid4())
        self.video_path = video_path
        self.start_time = 0.0
        self.end_time = None
        self.speed = 1.0
        self.is_reversed = False
        self.effects = []
        self.error = None
        
        # Node connections
        self.next_node = None
        self.prev_node = None
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        if not os.path.exists(video_path):
            self.error = f"Video file not found: {video_path}"
            self.logger.error(self.error)
            return
        
        # Initialize video properties
        self.duration = 0  # Duration in seconds
        self.frame_count = 0
        self.fps = 0
        self.width = 0
        self.height = 0
        
        self.load_video_info()
    
    def load_video_info(self):
        """Load basic video information."""
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error = f"Could not open video: {self.video_path}"
                self.logger.error(self.error)
                return
            
            # Get video properties
            self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate duration
            if self.fps > 0:
                self.duration = self.frame_count / self.fps
            else:
                self.error = f"Invalid FPS for video: {self.video_path}"
                self.logger.error(self.error)
            
            # Set end time if not set
            if self.end_time is None:
                self.end_time = self.duration
            
            cap.release()
            
        except Exception as e:
            self.error = f"Error loading video info: {str(e)}"
            self.logger.error(self.error)
            self.duration = 0
            self.frame_count = 0
            self.fps = 0
            self.width = 0
            self.height = 0
    
    def get_frame_at_time(self, time_pos: float) -> np.ndarray:
        """Get the frame at the specified time position."""
        if not self.video_path:
            return np.zeros((720, 1280, 3), dtype=np.uint8)
            
        # Apply time transformations
        if self.is_reversed:
            time_pos = self.duration - time_pos
            
        time_pos *= self.speed
        
        # Ensure time is within bounds
        time_pos = max(0, min(time_pos, self.duration))
        
        frame_number = int(time_pos * self.fps)
        frame = self.get_frame(frame_number)
        
        if frame is None:
            return np.zeros((720, 1280, 3), dtype=np.uint8)
        
        # Apply effects
        for effect in self.effects:
            frame = effect.apply(frame)
            
        return frame
    
    def get_frame(self, frame_number):
        """Get a specific frame from the video."""
        if self.error:
            self.logger.error(f"Cannot get frame, video has error: {self.error}")
            return None
            
        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.logger.error(f"Could not open video for frame extraction: {self.video_path}")
                return None
            
            # Set frame position
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame_rgb
            else:
                self.logger.error(f"Could not read frame {frame_number} from {self.video_path}")
                return None
            
        except Exception as e:
            self.logger.error(f"Error getting frame {frame_number} from {self.video_path}: {e}")
            return None
    
    def get_preview_frame(self):
        """Get a frame for preview purposes."""
        return self.get_frame(0)
    
    def add_effect(self, effect):
        """Add an effect to the video node."""
        self.effects.append(effect)
        self.state_changed.emit()
    
    def remove_effect(self, effect):
        """Remove an effect from the video node."""
        if effect in self.effects:
            self.effects.remove(effect)
            self.state_changed.emit()
    
    def set_time_range(self, start: float, end: float):
        """Set the time range for this clip."""
        self.start_time = max(0, start)
        self.end_time = min(self.duration, end)
        self.state_changed.emit()
    
    def set_speed(self, speed: float):
        """Set the playback speed of the clip."""
        self.speed = max(0.1, min(10.0, speed))
        self.state_changed.emit()
    
    def toggle_reverse(self):
        """Toggle reverse playback of the clip."""
        self.is_reversed = not self.is_reversed
        self.state_changed.emit()
    
    def get_duration(self) -> float:
        """Get the actual duration considering speed and time range."""
        base_duration = self.end_time - self.start_time
        return base_duration / self.speed
    
    def to_dict(self) -> dict:
        """Convert the node to a dictionary for serialization."""
        return {
            'id': self.id,
            'video_path': self.video_path,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'speed': self.speed,
            'is_reversed': self.is_reversed,
            'effects': [effect.to_dict() for effect in self.effects]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'VideoNode':
        """Create a node from a dictionary."""
        node = cls(data['video_path'])
        node.id = data['id']
        node.start_time = data['start_time']
        node.end_time = data['end_time']
        node.speed = data['speed']
        node.is_reversed = data['is_reversed']
        # Effects will be added when effect system is implemented
        return node
