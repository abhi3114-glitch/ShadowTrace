import time
import asyncio
# winsdk may require specific submodules to be installed or accessible
try:
    from winsdk.windows.devices.sensors import Accelerometer, LightSensor
except ImportError:
    print("winsdk not installed or modules missing")
    exit(1)

async def main():
    print("Checking sensors...")
    
    # ACCELEROMETER
    try:
        accel = Accelerometer.get_default()
        if accel:
            print("Accelerometer: FOUND")
            # Minimal reading
            reading = accel.get_current_reading()
            if reading:
                print(f"  Reading: X={reading.acceleration_x:.2f}, Y={reading.acceleration_y:.2f}, Z={reading.acceleration_z:.2f}")
            else:
                print("  Reading: None (Sensor might be initializing)")
        else:
            print("Accelerometer: NOT FOUND")
    except Exception as e:
        print(f"Accelerometer Error: {e}")

    # LIGHT SENSOR
    try:
        light = LightSensor.get_default()
        if light:
            print("Light Sensor: FOUND")
            reading = light.get_current_reading()
            if reading:
                print(f"  Reading: {reading.illuminance_in_lux} lux")
            else:
                print("  Reading: None")
        else:
            print("Light Sensor: NOT FOUND")
    except Exception as e:
        print(f"Light Sensor Error: {e}")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
