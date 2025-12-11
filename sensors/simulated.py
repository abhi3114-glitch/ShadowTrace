import time
import random
import math
from datetime import datetime
from .base import BaseSensor, SensorReading

class SimulatedSensor(BaseSensor):
    def __init__(self):
        self.running = False
        self._last_update = time.time()
        
        # State for simulation
        self.x = 0.0
        self.y = 9.8  # Resting on table roughly
        self.z = 0.0
        self.light = 300.0
        
        # Movement state
        self.phase = "idle" # idle, moving
        self.phase_duration = 0
        self.phase_start = 0

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def _update_simulation(self):
        now = time.time()
        dt = now - self._last_update
        self._last_update = now
        
        # Simple state machine to toggle between "working" (stationary) and "moving" (walking/adjusting)
        if now - self.phase_start > self.phase_duration:
            self.phase_start = now
            if self.phase == "idle":
                # Switch to moving potentially
                if random.random() < 0.3: # 30% chance to start moving
                    self.phase = "moving"
                    self.phase_duration = random.uniform(2, 10) # Move for 2-10 seconds
                else:
                    self.phase_duration = random.uniform(5, 30) # Stay idle
            else:
                # Switch back to idle
                self.phase = "idle"
                self.phase_duration = random.uniform(10, 60)

        # Generate noise based on phase
        if self.phase == "idle":
            # Micro jitters
            self.x = random.gauss(0, 0.05)
            self.y = random.gauss(9.8, 0.05)
            self.z = random.gauss(0, 0.05)
            # Light stays relatively stable
            self.light += random.uniform(-1, 1)
        else:
            # Larger movements
            self.x = random.gauss(0, 2.0) + math.sin(now * 3) # Periodic sway
            self.y = random.gauss(9.8, 2.0)
            self.z = random.gauss(0, 2.0)
            # Light varies more (shadows passing)
            self.light += random.uniform(-20, 20)
        
        # Clamp light
        self.light = max(0, min(2000, self.light))
        
        # Heuristic for "is_moving"
        magnitude = math.sqrt(self.x**2 + (self.y - 9.8)**2 + self.z**2)
        is_moving = magnitude > 0.5 

        return SensorReading(
            timestamp=datetime.now(),
            acc_x=self.x,
            acc_y=self.y,
            acc_z=self.z,
            light_level=self.light,
            is_moving=is_moving
        )

    def get_reading(self) -> SensorReading:
        if not self.running:
            return None
        return self._update_simulation()
