import numpy as np
import cv2
from .base_effect import BaseEffect

class RotateEffect(BaseEffect):
    """Rotate the frame by a specified angle."""
    
    def __init__(self, angle: float = 0.0):
        super().__init__()
        self.angle = angle
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled or self.angle == 0:
            return frame
            
        height, width = frame.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        matrix = cv2.getRotationMatrix2D(center, self.angle, 1.0)
        
        # Calculate new dimensions
        cos = np.abs(matrix[0, 0])
        sin = np.abs(matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Adjust matrix
        matrix[0, 2] += (new_width / 2) - center[0]
        matrix[1, 2] += (new_height / 2) - center[1]
        
        # Apply rotation
        return cv2.warpAffine(frame, matrix, (new_width, new_height))
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['angle'] = self.angle
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'RotateEffect':
        effect = super().from_dict(data)
        effect.angle = data['angle']
        return effect

class ScaleEffect(BaseEffect):
    """Scale the frame by a specified factor."""
    
    def __init__(self, scale_x: float = 1.0, scale_y: float = 1.0):
        super().__init__()
        self.scale_x = max(0.1, scale_x)
        self.scale_y = max(0.1, scale_y)
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled or (self.scale_x == 1.0 and self.scale_y == 1.0):
            return frame
            
        height, width = frame.shape[:2]
        new_size = (int(width * self.scale_x), int(height * self.scale_y))
        return cv2.resize(frame, new_size, interpolation=cv2.INTER_LANCZOS4)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'scale_x': self.scale_x,
            'scale_y': self.scale_y
        })
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScaleEffect':
        effect = super().from_dict(data)
        effect.scale_x = data['scale_x']
        effect.scale_y = data['scale_y']
        return effect

class CropEffect(BaseEffect):
    """Crop the frame to a specified region."""
    
    def __init__(self, x: float = 0.0, y: float = 0.0, width: float = 1.0, height: float = 1.0):
        super().__init__()
        self.x = max(0.0, min(1.0, x))
        self.y = max(0.0, min(1.0, y))
        self.width = max(0.0, min(1.0 - self.x, width))
        self.height = max(0.0, min(1.0 - self.y, height))
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled or (self.x == 0 and self.y == 0 and self.width == 1 and self.height == 1):
            return frame
            
        h, w = frame.shape[:2]
        x1 = int(w * self.x)
        y1 = int(h * self.y)
        x2 = int(w * (self.x + self.width))
        y2 = int(h * (self.y + self.height))
        
        return frame[y1:y2, x1:x2]
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data.update({
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        })
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CropEffect':
        effect = super().from_dict(data)
        effect.x = data['x']
        effect.y = data['y']
        effect.width = data['width']
        effect.height = data['height']
        return effect
