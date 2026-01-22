import sys
import os
import time

# Add local directory to path to find core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.sensors import UltrasonicSensor

def test_sensor():
    print("Testing Ultrasonic Sensor (via gpiozero)...")
    print("Press Ctrl+C to stop.")
    
    sensor = None
    try:
        sensor = UltrasonicSensor(trigger_pin=23, echo_pin=24)
        
        while True:
            dist = sensor.measure_distance()
            if dist == -1:
                # debug dots to show it's alive
                # print(".", end="", flush=True) 
                pass
            else:
                print(f"Distance: {dist} cm")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if sensor:
            print("Cleaning up...")
            sensor.cleanup()

if __name__ == "__main__":
    test_sensor()
