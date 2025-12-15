import os
import cv2
import face_recognition
import pickle
import sys
# Ensure core can be imported if running this script directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database import init_db, Student

def train_model(dataset_dir='dataset', model_path='encodings.pickle'):
    print(f"Starting training on '{dataset_dir}'...")
    
    # Initialize DB connection
    try:
        session = init_db()
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return

    # Clear existing student data to ensure DB matches dataset
    try:
        deleted_count = session.query(Student).delete()
        session.commit()
        print(f"Cleared {deleted_count} existing student records from database.")
    except Exception as e:
        print(f"Warning: Failed to clear old data: {e}")
        session.rollback()

    # Check if dataset dir exists
    if not os.path.exists(dataset_dir):
        print(f"Dataset directory '{dataset_dir}' not found. Please create it and add subfolders with images.")
        # Create it for convenience
        os.makedirs(dataset_dir)
        print(f"Created empty directory '{dataset_dir}'.")
        return

    known_encodings = []
    known_names = []

    # Iterate over person folders
    for name in os.listdir(dataset_dir):
        person_dir = os.path.join(dataset_dir, name)
        if not os.path.isdir(person_dir):
            continue

        print(f"Processing images for {name}...")
        image_count = 0
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            
            # Simple extension check
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            try:
                # Load image
                image = cv2.imread(filepath)
                if image is None:
                    print(f"Warning: Could not read image {filename}")
                    continue
                
                # Convert to RGB (face_recognition expects RGB)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                
                # Detect faces
                boxes = face_recognition.face_locations(rgb, model='hog')
                encodings = face_recognition.face_encodings(rgb, boxes)

                if len(encodings) > 0:
                    # Use the first face found
                    encoding = encodings[0]
                    known_encodings.append(encoding)
                    known_names.append(name)
                    
                    # Serialize encoding for DB
                    encoding_blob = pickle.dumps(encoding)
                    
                    # Add to Database
                    student = Student(name=name, encoding=encoding_blob)
                    session.add(student)
                    image_count += 1
                else:
                    print(f"No face found in {filename} - skipping.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
        
        print(f"Added {image_count} face encodings for {name}.")

    try:
        session.commit()
        print("Database updated successfully.")
    except Exception as e:
        print(f"Error committing to database: {e}")
        session.rollback()
    
    # Save to .pickle file as requested
    data = {"encodings": known_encodings, "names": known_names}
    try:
        with open(model_path, "wb") as f:
            f.write(pickle.dumps(data))
        print(f"Encodings also saved to {model_path}")
    except Exception as e:
        print(f"Error saving pickle file: {e}")
    
    print("Training complete.")

if __name__ == "__main__":
    train_model()
