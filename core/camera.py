import abc
import cv2
import platform
import numpy as np

class CameraInterface(abc.ABC):
    @abc.abstractmethod
    def get_frame(self):
        """Returns a frame in BGR format (for OpenCV compatibility)"""
        pass

    @abc.abstractmethod
    def stop(self):
        pass

class DesktopCamera(CameraInterface):
    def __init__(self, source=0):
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            # Try to force open? raise?
            print(f"Warning: Unable to open camera source {source}")
    
    def get_frame(self):
        if not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def stop(self):
        if self.cap.isOpened():
            self.cap.release()

class PiCamera(CameraInterface):
    def __init__(self):
        try:
            from picamera2 import Picamera2 # type: ignore
            print("Initializing Picamera2...")
            self.picam2 = Picamera2()
            # Use preview configuration for continuous video capture (RGB888 for OpenCV compatibility)
            config = self.picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
            self.picam2.configure(config)
            self.picam2.start()
            print("Picamera2 started successfully.")
        except ImportError as e:
            raise ImportError(f"Picamera2 is not installed or supported on this system: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Picamera2: {e}")

    def get_frame(self):
        try:
            # Capture array in RGB888 format
            frame = self.picam2.capture_array()
            # Convert RGB to BGR for OpenCV compatibility
            return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"PiCamera Error: {e}")
            return None

    def stop(self):
        if hasattr(self, 'picam2'):
            self.picam2.stop()
            print("Picamera2 stopped.")

class CameraFactory:
    @staticmethod
    def create_camera():
        # Check for Raspberry Pi
        is_pi = False
        try:
            with open('/proc/device-tree/model', 'r') as f:
                if 'Raspberry Pi' in f.read():
                    is_pi = True
        except (IOError, FileNotFoundError):
            pass

        if is_pi:
            try:
                print("Raspberry Pi detected. Initializing PiCamera.")
                return PiCamera()
            except Exception as e:
                print(f"Failed to initialize PiCamera: {e}. Fallback to DesktopCamera.")
                return DesktopCamera()
        else:
            print("Desktop environment detected. Using DesktopCamera.")
            return DesktopCamera()
