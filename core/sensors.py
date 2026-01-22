from gpiozero import DistanceSensor
import time

class UltrasonicSensor:
    def __init__(self, trigger_pin=23, echo_pin=24):
        """
        Initialize the Ultrasonic Sensor using gpiozero (Pi 5 Compatible).
        
        Args:
            trigger_pin (int): GPIO pin connected to the Trigger on the sensor.
            echo_pin (int): GPIO pin connected to the Echo on the sensor.
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.sensor = None
        
        try:
            # gpiozero uses BCM numbering by default
            # max_distance=4 means 4 meters max (default is 1)
            # threshold_distance default is 0.3m. 
            self.sensor = DistanceSensor(echo=echo_pin, trigger=trigger_pin, max_distance=4)
            print(f"Ultrasonic Sensor initialized via gpiozero (Trig:{trigger_pin}, Echo:{echo_pin})")
        except Exception as e:
            print(f"Error initializing Ultrasonic Sensor: {e}")

    def measure_distance(self):
        """
        Measure distance in centimeters.
        
        Returns:
            float: Distance in cm, or -1 if measurement fails/timeouts.
        """
        if not self.sensor:
            return -1
            
        try:
            # gpiozero returns distance in meters.
            # value property returns current distance value. 
            # If it's effectively None or issues, it might raise errors or return nothing?
            # actually .distance returns float in meters
            
            dist_m = self.sensor.distance
            
            # Convert to cm
            dist_cm = dist_m * 100
            
            # Simple validity check
            if dist_cm <= 0 or dist_cm > 400:
                # Sometimes startup gives 0
                return -1
                
            return round(dist_cm, 2)
            
        except Exception as e:
            # gpiozero handles IO errors internally usually, but just in case
            # It might return 1.0 (max) if no object? 
            # We just print debug if it's a real error
            # print(f"Error reading sensor: {e}")
            return -1

    def cleanup(self):
        """Clean up resources."""
        if self.sensor:
            self.sensor.close()

