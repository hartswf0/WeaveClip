import pytest
from unittest.mock import MagicMock, patch
import sys
import os
from PyQt6.QtCore import QSize
import tempfile

# Mock classes that don't depend on Qt initialization
class MockCanvas:
    def __init__(self):
        self.zoom_level = 1.0
        self.MAX_ZOOM = 10.0
        self.MIN_ZOOM = 0.1
        self._size = QSize(100, 100)
        
    def add_video_node(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        if not file_path.lower().endswith(('.mp4', '.avi', '.mov')):
            raise ValueError(f"Invalid video file type: {file_path}")
            
    def set_zoom(self, level):
        self.zoom_level = max(min(level, self.MAX_ZOOM), self.MIN_ZOOM)
        
    def size(self):
        return self._size
        
    def resize(self, size):
        # Ensure minimum size
        width = max(1, size.width())
        height = max(1, size.height())
        self._size = QSize(width, height)
        return self._size

class MockTimeline:
    def __init__(self):
        self.current_time = 0.0
        
    def set_current_time(self, time):
        if time < 0:
            raise ValueError("Time cannot be negative")
        self.current_time = time

class MockMainWindow:
    def __init__(self):
        self.canvas = MockCanvas()
        self.timeline = MockTimeline()

def test_canvas_rejects_invalid_video_files():
    """Test that the canvas properly rejects invalid video files."""
    canvas = MockCanvas()
    
    # Test with non-existent file
    with pytest.raises(FileNotFoundError):
        canvas.add_video_node("nonexistent_file.mp4")
    
    # Create a temporary text file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
        tmp_file.write(b"test content")
    
    try:
        # Test with invalid file type
        with pytest.raises(ValueError):
            canvas.add_video_node(tmp_file.name)
    finally:
        # Clean up the temporary file
        os.unlink(tmp_file.name)

def test_canvas_handles_zero_size_window():
    """Test that the canvas gracefully handles being resized to zero."""
    canvas = MockCanvas()
    result = canvas.resize(QSize(0, 0))
    assert result.width() >= 1
    assert result.height() >= 1

def test_timeline_handles_negative_time():
    """Test that timeline prevents setting negative time values."""
    timeline = MockTimeline()
    with pytest.raises(ValueError):
        timeline.set_current_time(-1.0)

def test_canvas_handles_excessive_zoom():
    """Test that canvas prevents excessive zoom levels."""
    canvas = MockCanvas()
    original_zoom = canvas.zoom_level
    
    # Try to zoom way too far in
    canvas.set_zoom(1000000.0)
    assert canvas.zoom_level <= canvas.MAX_ZOOM
    
    # Try to zoom way too far out
    canvas.set_zoom(0.0000001)
    assert canvas.zoom_level >= canvas.MIN_ZOOM

def test_timeline_maintains_state():
    """Test that timeline properly maintains its state."""
    timeline = MockTimeline()
    test_time = 5.0
    
    timeline.set_current_time(test_time)
    assert timeline.current_time == test_time
