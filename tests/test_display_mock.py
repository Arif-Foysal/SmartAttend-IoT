import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.display import DisplayManager

def test_display():
    print("Initializing DisplayManager...")
    dm = DisplayManager()
    
    print("Testing show_attendance (Call 1)...")
    dm.show_attendance("Test User", "12345")
    
    print("Testing show_attendance (Call 2 - Immediate)...")
    # This should NOT print [OLED MOCK] again if optimized
    dm.show_attendance("Test User", "12345")
    
    print("Waiting 2 seconds...")
    import time
    time.sleep(2)
    
    print("Testing show_attendance (Call 3 - Extended)...")
    # This should ALSO NOT print [OLED MOCK], but should extend timer
    dm.show_attendance("Test User", "12345")
    
    print("Waiting 4 seconds to verify auto-clear...")
    time.sleep(4)
    
    print("Test Complete.")

if __name__ == "__main__":
    test_display()
