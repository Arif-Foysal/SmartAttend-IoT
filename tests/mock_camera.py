import numpy as np
import cv2
import sys
import os
# Ensure core can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.camera import CameraInterface

class MockCamera(CameraInterface):
    def __init__(self):
        print("Initializing Mock Camera")
        self.frame_count = 0
    
    def get_frame(self):
        # Create a blank image 640x480 (BGR)
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Add a moving rectangle to simulate "video"
        x = (self.frame_count * 5) % 580
        cv2.rectangle(img, (x, 200), (x + 60, 260), (0, 255, 0), -1)
        
        # Add some text
        cv2.putText(img, f"Frame {self.frame_count}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        self.frame_count += 1
        return img

    def stop(self):
        print("Mock Camera Stopped")
