import cv2
import face_recognition
import threading
import pickle
import time
from datetime import datetime, timedelta
import numpy as np
from core.api_client import APIClient

class FaceRecognizer:
    def __init__(self, api_url='http://localhost:8000'):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.api_client = APIClient(api_url)
        self.load_encodings()
        
        self.frame_to_process = None
        self.frame_lock = threading.Lock()
        
        self.current_locations = []
        self.current_names = []
        self._stop_event = threading.Event()
        
        self.last_seen = {} # {student_id: datetime}
        self.debounce_period = timedelta(minutes=10)

    def load_encodings(self):
        """Load encoded faces from the API."""
        print("Fetching encodings from backend...")
        try:
            students = self.api_client.fetch_students()
            for student in students:
                self.known_face_encodings.append(student['encoding'])
                self.known_face_names.append(student['name'])
                self.known_face_ids.append(student['id'])
            print(f"Loaded {len(self.known_face_encodings)} known faces.")
        except Exception as e:
            print(f"Error loading encodings: {e}")

    def start(self):
        """Start the background processing thread."""
        self._stop_event.clear()
        self.thread = threading.Thread(target=self.process_loop, daemon=True)
        self.thread.start()
        
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.sync_thread.start()

    def stop(self):
        """Stop the background processing thread."""
        self._stop_event.set()
        if hasattr(self, 'thread'):
            self.thread.join()
        if hasattr(self, 'sync_thread'):
            self.sync_thread.join()

    def sync_loop(self):
        """Background loop to sync encodings periodically."""
        while not self._stop_event.is_set():
            # Wait for 300 seconds, or until stop event is set
            if self._stop_event.wait(timeout=300):
                break
            
            print("Auto-syncing encodings...")
            self.load_encodings()

    def process_frame(self, frame):
        """Update the frame to be processed by the background thread.
           This should be called from the main thread loop."""
        with self.frame_lock:
            # We copy to avoid concurrent modification issues if the main thread modifies it
            # although usually main captures new frames.
            self.frame_to_process = frame.copy()

    def get_results(self):
        """Get the latest recognition results (locations, names)."""
        return self.current_locations, self.current_names

    def process_loop(self):
        """Background loop that processes frames."""
        while not self._stop_event.is_set():
            frame = None
            with self.frame_lock:
                if self.frame_to_process is not None:
                    frame = self.frame_to_process
                    self.frame_to_process = None # Clear pending frame
            
            if frame is None:
                time.sleep(0.01) # Avoid busy waiting
                continue
                
            try:
                # Resize to 1/4 size for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                
                # Convert BGR (OpenCV) to RGB (face_recognition)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # Default
                    name = "Unknown"
                    student_id = None
                    
                    if len(self.known_face_encodings) > 0:
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        
                        if len(face_distances) > 0:
                            best_match_index = np.argmin(face_distances)
                            if matches[best_match_index]:
                                name = self.known_face_names[best_match_index]
                                student_id = self.known_face_ids[best_match_index]
                                self.log_attendance(student_id, name)

                    face_names.append(name)

                self.current_locations = face_locations
                self.current_names = face_names
                
            except Exception as e:
                print(f"Error in recognition loop: {e}")

    def log_attendance(self, student_id, name):
        """Log attendance with debouncing logic."""
        now = datetime.now()
        last_time = self.last_seen.get(student_id)
        
        if last_time is None or (now - last_time) > self.debounce_period:
            print(f"Logging attendance for {name} at {now}")
            success = self.api_client.log_attendance(student_id, name, now)
            if success:
                self.last_seen[student_id] = now
            else:
                # If API fails, we still debounce to avoid flooding the server with error requests
                print("Failed to sync attendance. Retrying later.")
                self.last_seen[student_id] = now
        else:
            # Debounced (ignored)
            pass
