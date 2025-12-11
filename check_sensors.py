import sys

def check():
    print(f"Python: {sys.version}")
    try:
        from sensors.windows_native import WindowsNativeSensor
        print("Module 'sensors.windows_native' imported.")
        
        sensor = WindowsNativeSensor()
        sensor.start()
        
        acc = sensor.accelerometer
        light = sensor.light_sensor
        
        if acc:
            print(f"Accelerometer: FOUND ({acc})")
        else:
            print("Accelerometer: NOT FOUND")
            
        if light:
            print(f"Light Sensor: FOUND ({light})")
        else:
            print("Light Sensor: NOT FOUND")
            
        sensor.stop()
        
        if acc:
            print("RESULT: Real Sensors should be active.")
        else:
            print("RESULT: Fallback to Simulation.")
            
    except ImportError as e:
        print(f"ImportError: {e}")
        print("RESULT: Fallback to Simulation.")
    except Exception as e:
        print(f"Error: {e}")
        print("RESULT: Fallback to Simulation.")

if __name__ == "__main__":
    check()
