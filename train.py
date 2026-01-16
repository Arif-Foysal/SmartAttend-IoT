import os
import sys
import requests

# Ensure we can import from core if needed, though we primarily use requests now
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

API_URL = "http://localhost:8000"

def train_model(dataset_dir='dataset'):
    print(f"Starting training from '{dataset_dir}' via API at {API_URL}...")
    
    # Check if dataset dir exists
    if not os.path.exists(dataset_dir):
        print(f"Dataset directory '{dataset_dir}' not found. Creating it...")
        os.makedirs(dataset_dir)
        print("Please add student folders with images to the 'dataset' directory and run this script again.")
        return

    # Check API connection
    try:
        requests.get(API_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to backend at {API_URL}. Please ensure 'main.py' (backend) is running.")
        return

    # 1. Wipe existing data
    print("Clearing existing student data...")
    try:
        # Fetch all students
        resp = requests.get(f"{API_URL}/students/?limit=1000")
        if resp.status_code == 200:
            students = resp.json()
            for s in students:
                print(f"Deleting {s['name']} (ID: {s['id']})...")
                requests.delete(f"{API_URL}/students/{s['id']}")
        else:
            print(f"Warning: Failed to fetch existing students: {resp.text}")
    except Exception as e:
        print(f"Error clearing data: {e}")
        return

    # 2. Upload new data
    processed_count = 0
    
    for name in os.listdir(dataset_dir):
        person_dir = os.path.join(dataset_dir, name)
        if not os.path.isdir(person_dir):
            continue

        images = [f for f in os.listdir(person_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            print(f"Skipping {name}: No images found.")
            continue
            
        print(f"Processing {name} ({len(images)} images)...")
        
        student_id = None
        
        # Create student with first image
        first_image = images[0]
        try:
            with open(os.path.join(person_dir, first_image), 'rb') as f:
                files = {'photo': (first_image, f, 'image/jpeg')}
                data = {'name': name}
                resp = requests.post(f"{API_URL}/students/", data=data, files=files)
                
                if resp.status_code == 200:
                    student_data = resp.json()
                    student_id = student_data['id']
                else:
                    print(f"Failed to create student {name}: {resp.text}")
                    continue
        except Exception as e:
            print(f"Error uploading {name}: {e}")
            continue

        # Upload remaining images
        for img_file in images[1:]:
            try:
                with open(os.path.join(person_dir, img_file), 'rb') as f:
                    files = {'photo': (img_file, f, 'image/jpeg')}
                    resp = requests.post(f"{API_URL}/students/{student_id}/images", files=files)
                    if resp.status_code != 200:
                        print(f"Warning: Failed to upload extra image for {name}: {resp.text}")
            except Exception as e:
                 print(f"Error uploading image for {name}: {e}")

        processed_count += 1

    print(f"Training complete. Processed {processed_count} students.")

if __name__ == "__main__":
    train_model()
