import sys
import os
import time

# Add local directory to path to find core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.buzzer import SystemBuzzer

def test_buzzer():
    print("Testing Buzzer on GPIO 17...")
    
    try:
        buzzer = SystemBuzzer(pin=17)
        
        print("Playing Success Beep (Double Beep)...")
        buzzer.beep_success()
        time.sleep(2)
        
        print("Playing Error Beep (Long Beep)...")
        buzzer.beep_error()
        time.sleep(2)
        
        print("Test Complete.")
        buzzer.cleanup()
        
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_buzzer()
