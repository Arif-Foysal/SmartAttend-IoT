import cv2

print("Testing camera indices 0-10...")
for i in range(11):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"Index {i}: SUCCESS. Frame shape: {frame.shape}")
        else:
            print(f"Index {i}: Failed to read frame (isOpened=True)")
        cap.release()
    else:
        print(f"Index {i}: Failed to open")
