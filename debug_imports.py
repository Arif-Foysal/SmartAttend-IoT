import sys
print(sys.path)
try:
    import face_recognition_models
    print(f"Success model: {face_recognition_models.__file__}")
except ImportError as e:
    print(f"Error model: {e}")

try:
    import face_recognition
    print("Success lib: face_recognition imported")
except Exception as e:
    print(f"Error lib: {e}")
