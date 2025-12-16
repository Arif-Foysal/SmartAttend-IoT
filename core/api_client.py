import requests
import pickle
import time
import base64
from datetime import datetime

class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        
    def fetch_students(self):
        """Fetch all student encodings from the backend.
        Returns: List of (id, name, encoding_numpy)
        """
        try:
            response = requests.get(f"{self.base_url}/students/sync", timeout=10)
            if response.status_code == 200:
                students_data = response.json()
                parsed_students = []
                for s in students_data:
                    try:
                        # 1. Base64 decode
                        pickled_bytes = base64.b64decode(s['encoding'])
                        # 2. Pickle load
                        encoding = pickle.loads(pickled_bytes)
                        
                        parsed_students.append({
                            'id': s['id'],
                            'name': s['name'],
                            'encoding': encoding
                        })
                    except Exception as parse_err:
                        print(f"Error parsing student {s.get('name')}: {parse_err}")
                        
                return parsed_students
            else:
                print(f"Failed to fetch students: {response.text}")
                return []
        except Exception as e:
            print(f"API Error fetching students: {e}")
            return []

    def log_attendance(self, student_id, name, timestamp=None):
        """Send attendance log to backend."""
        if timestamp is None:
            timestamp = datetime.now()
            
        payload = {
            "student_id": student_id,
            "timestamp": timestamp.isoformat(),
            "device_id": "device_001" # TODO: Configurable
        }
        
        try:
            response = requests.post(f"{self.base_url}/attendance/", json=payload, timeout=5)
            if response.status_code == 200:
                print(f"Logged {name} remote success.")
                return True
            else:
                print(f"Failed to log {name}: {response.text}")
                return False
        except Exception as e:
            print(f"API Error logging attendance: {e}")
            return False
