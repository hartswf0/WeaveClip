from abc import ABC, abstractmethod
import numpy as np
import uuid

class BaseEffect(ABC):
    """Base class for all video effects."""
    
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.enabled = True
    
    @abstractmethod
    def apply(self, frame: np.ndarray) -> np.ndarray:
        """Apply the effect to a frame.
        
        Args:
            frame: Input frame as numpy array (height, width, channels)
            
        Returns:
            Modified frame as numpy array
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convert the effect to a dictionary for serialization."""
        return {
            'id': self.id,
            'type': self.__class__.__name__,
            'enabled': self.enabled
        }
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> 'BaseEffect':
        """Create an effect from a dictionary."""
        effect = cls()
        effect.id = data['id']
        effect.enabled = data['enabled']
        return effect
