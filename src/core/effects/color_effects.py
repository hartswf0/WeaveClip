import numpy as np
import cv2
from .base_effect import BaseEffect

class BrightnessEffect(BaseEffect):
    """Adjust the brightness of a frame."""
    
    def __init__(self, value: float = 0.0):
        super().__init__()
        self.value = max(-1.0, min(1.0, value))
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return frame
            
        if self.value > 0:
            return cv2.addWeighted(frame, 1, np.zeros_like(frame), 0, self.value * 255)
        else:
            return cv2.addWeighted(frame, 1 + self.value, np.zeros_like(frame), 0, 0)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['value'] = self.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BrightnessEffect':
        effect = super().from_dict(data)
        effect.value = data['value']
        return effect

class ContrastEffect(BaseEffect):
    """Adjust the contrast of a frame."""
    
    def __init__(self, value: float = 1.0):
        super().__init__()
        self.value = max(0.0, min(3.0, value))
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return frame
            
        return cv2.convertScaleAbs(frame, alpha=self.value, beta=0)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['value'] = self.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ContrastEffect':
        effect = super().from_dict(data)
        effect.value = data['value']
        return effect

class SaturationEffect(BaseEffect):
    """Adjust the saturation of a frame."""
    
    def __init__(self, value: float = 1.0):
        super().__init__()
        self.value = max(0.0, min(3.0, value))
    
    def apply(self, frame: np.ndarray) -> np.ndarray:
        if not self.enabled:
            return frame
            
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:, :, 1] *= self.value
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
    
    def to_dict(self) -> dict:
        data = super().to_dict()
        data['value'] = self.value
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SaturationEffect':
        effect = super().from_dict(data)
        effect.value = data['value']
        return effect
