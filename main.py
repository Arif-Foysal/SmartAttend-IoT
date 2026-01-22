import cv2
import time
import sys
import os

# Add local directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.camera import CameraFactory
from core.recognition import FaceRecognizer

def main():
    print("Initializing SmartAttend-IoT System...")
    
    # Initialize Camera
    try:
        camera = CameraFactory.create_camera()
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return

    # Initialize Face Recognizer
    try:
        recognizer = FaceRecognizer()
        recognizer.start()
        print("Face Recognition engine started.")
    except Exception as e:
        print(f"Error initializing recognition engine: {e}")
        camera.stop()
        return

    # Initialize Ultrasonic Sensor
    try:
        from core.sensors import UltrasonicSensor
        sensor = UltrasonicSensor()
        print("Ultrasonic Sensor initialized.")
    except Exception as e:
        print(f"Error initializing sensor: {e}")
        sensor = None

    print("Starting main loop. Press 'q' to quit.")
    
    # Sleep/Wake Logic variables
    last_active_time = time.time()
    SLEEP_TIMEOUT = 5 # seconds (Reduced for faster sleep)
    is_sleeping = False
    
    try:
        while True:
            # Check sensor if available
            if sensor:
                dist = sensor.measure_distance()
                # If object is close (< 50cm), reset timer
                if dist > 0 and dist < 50:
                    last_active_time = time.time()
                    if is_sleeping:
                        print("Motion detected! Waking up...")
                        is_sleeping = False

            # Check for sleep timeout
            if not is_sleeping and (time.time() - last_active_time > SLEEP_TIMEOUT):
                print("No activity. Going to sleep...")
                is_sleeping = True
                
            if is_sleeping:
                # Sleep mode: Show message
                import numpy as np
                # Create black image (480x640 is typical, we can query camera but let's assume standard VGA or just generic)
                # Better: get shape from last frame if possible, or default
                h, w = 480, 640
                if 'frame' in locals() and frame is not None:
                     h, w = frame.shape[:2]
                
                sleep_frame = np.zeros((h, w, 3), np.uint8)
                
                # Centered Text
                text = "System Sleeping..."
                font = cv2.FONT_HERSHEY_DUPLEX
                font_scale = 1.0
                thickness = 2
                (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
                
                text_x = (w - text_w) // 2
                text_y = (h + text_h) // 2
                
                cv2.putText(sleep_frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), thickness)
                cv2.putText(sleep_frame, "Wave to wake up", (text_x, text_y + 40), font, 0.7, (200, 200, 200), 1)

                cv2.imshow('SmartAttend Face Recognition', sleep_frame)

                # WaitKey is essential for imshow to work
                # Sleep a bit to save CPU (200ms = 5fps update for the text)
                if cv2.waitKey(200) & 0xFF == ord('q'):
                    break
                continue

            # --- ACTIVE MODE ---
            
            # Capture frame
            frame = camera.get_frame()
            if frame is None:
                # print("No frame")
                time.sleep(0.01)
                continue
            
            # Send frame to background recognizer
            recognizer.process_frame(frame)
            
            # Get latest results from recognizer
            locations, names = recognizer.get_results()
            
            # Draw results on frame for UI
            for (top, right, bottom, left), name in zip(locations, names):
                # Scale coordinates back up (recognition runs at 1/4 scale)
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Draw box
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                
                # Draw label
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            
            # Show live feed
            cv2.imshow('SmartAttend Face Recognition', frame)
            
            # Standard 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        print("\nStopping by User Interrupt...")
    finally:
        print("Cleaning up resources...")
        recognizer.stop()
        camera.stop()
        if sensor:
             sensor.cleanup()
        cv2.destroyAllWindows()
        print("System stopped successfully.")

if __name__ == "__main__":
    main()
