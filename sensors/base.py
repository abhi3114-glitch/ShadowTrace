from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class SensorReading:
    timestamp: datetime
    acc_x: float
    acc_y: float
    acc_z: float
    light_level: float
    is_moving: bool

class BaseSensor(ABC):
    @abstractmethod
    def start(self):
        """Start sensor polling or initialization."""
        pass

    @abstractmethod
    def stop(self):
        """Stop sensor polling."""
        pass

    @abstractmethod
    def get_reading(self) -> Optional[SensorReading]:
        """Return the latest sensor reading."""
        pass
