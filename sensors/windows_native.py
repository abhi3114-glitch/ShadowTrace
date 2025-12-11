import time
import asyncio
import threading
from datetime import datetime
from typing import Optional
from .base import BaseSensor, SensorReading

# Import winsdk modules at runtime or top level if guaranteed
import winsdk.windows.devices.sensors as sensors

class WindowsNativeSensor(BaseSensor):
    def __init__(self):
        self.running = False
        self.accelerometer = None
        self.light_sensor = None
        self._last_reading = None
        self._lock = threading.Lock()

    def start(self):
        try:
            self.accelerometer = sensors.Accelerometer.get_default()
            self.light_sensor = sensors.LightSensor.get_default()
            self.running = True
            print(f"WindowsNativeSensor: Accel={self.accelerometer is not None}, Light={self.light_sensor is not None}")
        except Exception as e:
            print(f"Failed to initialize Windows Sensors: {e}")
            self.running = False

    def stop(self):
        self.running = False
        self.accelerometer = None
        self.light_sensor = None

    def get_reading(self) -> Optional[SensorReading]:
        if not self.running:
            return None
        
        # Read Accelerometer
        acc_x, acc_y, acc_z = 0.0, 0.0, 0.0
        is_moving = False # We need to calculate this from diff or rely on a "Shaken" event if available, 
                          # but simpler to just read raw data and let analysis handle "is_moving" logic, 
                          # OR do simple diff here.
        
        if self.accelerometer:
            reading = self.accelerometer.get_current_reading()
            if reading:
                acc_x = reading.acceleration_x
                acc_y = reading.acceleration_y
                acc_z = reading.acceleration_z

        # Read Light
        light_level = 0.0
        if self.light_sensor:
            l_reading = self.light_sensor.get_current_reading()
            if l_reading:
                light_level = l_reading.illuminance_in_lux

        # Simple movement detection (naive difference check would require state, 
        # for now let's just pass raw values and let the analyzer or a wrapper filter it.
        # But our interface requires 'is_moving'.
        # Let's implement a quick local diff.
        
        now = datetime.now()
        is_moving = False
        
        # Determine if moving based on simple magnitude variance or just pass True if magnitude != 1g
        # But easier: we keep state in the Class if needed. 
        # Let's do a simple magnitude check against 1.0 (assuming normalized Gs). 
        # Standard gravity is ~1.0 net vector. Significant deviation implies acceleration.
        magnitude = (acc_x**2 + acc_y**2 + acc_z**2)**0.5
        # Threshold: if dev is stationary flat, mag is 1.0. If moving, it fluctuates.
        # This is a very rough heuristic.
        is_moving = abs(magnitude - 1.0) > 0.1 # 10% deviation from 1g
        
        return SensorReading(
            timestamp=now,
            acc_x=acc_x,
            acc_y=acc_y,
            acc_z=acc_z,
            light_level=light_level,
            is_moving=is_moving
        )
