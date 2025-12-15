import time
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.recognition import FaceRecognizer
from tests.mock_camera import MockCamera

def verify():
    print("Starting System Verification...")
    
    # 1. Initialize FaceRecognizer (Tests DB connection and Threading)
    print("Initializing FaceRecognizer...")
    try:
        rec = FaceRecognizer()
        rec.start()
        print("FaceRecognizer started.")
    except Exception as e:
        print(f"FAILED to start FaceRecognizer: {e}")
        return
    
    # 2. Initialize Mock Camera (Tests Camera Interface)
    print("Initializing MockCamera...")
    try:
        cam = MockCamera()
    except Exception as e:
        print(f"FAILED to start MockCamera: {e}")
        rec.stop()
        return
    
    # 3. Run Loop for a few iterations (Tests Data Flow)
    print("Running process loop for 5 frames...")
    try:
        for i in range(5):
            frame = cam.get_frame()
            rec.process_frame(frame)
            
            # Allow some time for background thread
            time.sleep(0.2)
            
            locs, names = rec.get_results()
            print(f" [Frame {i}] Locations detected: {len(locs)} | Names: {names}")
            
    except Exception as e:
        print(f"Error during loop: {e}")
        
    # 4. Cleanup
    print("Stopping modules...")
    rec.stop()
    cam.stop()
    print("Verification Finished.")

if __name__ == "__main__":
    verify()
