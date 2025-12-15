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

    print("Starting main loop. Press 'q' to quit.")
    
    try:
        while True:
            # Capture frame
            frame = camera.get_frame()
            if frame is None:
                # print("No frame") # reduce spam
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
        cv2.destroyAllWindows()
        print("System stopped successfully.")

if __name__ == "__main__":
    main()
