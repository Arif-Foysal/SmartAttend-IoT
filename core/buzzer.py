from gpiozero import Buzzer
import time
import threading

class SystemBuzzer:
    def __init__(self, pin=17):
        """
        Initialize the Buzzer.
        
        Args:
            pin (int): GPIO pin connected to the positive leg of the buzzer.
        """
        self.pin = pin
        self.buzzer = None
        self.enabled = False
        
        try:
            self.buzzer = Buzzer(pin)
            self.enabled = True
            print(f"Buzzer initialized on GPIO {pin}")
        except Exception as e:
            print(f"Error initializing Buzzer: {e}")

    def beep_success(self):
        """Play a success sound (Double Beep). Non-blocking."""
        if not self.enabled:
            return
            
        def _play():
            try:
                self.buzzer.on()
                time.sleep(0.1)
                self.buzzer.off()
                time.sleep(0.1)
                self.buzzer.on()
                time.sleep(0.1)
                self.buzzer.off()
            except Exception as e:
                print(f"Buzzer error: {e}")

        # Run in thread to not block main loop
        threading.Thread(target=_play, daemon=True).start()

    def beep_error(self):
        """Play an error sound (Long Beep). Non-blocking."""
        if not self.enabled:
            return

        def _play():
            try:
                self.buzzer.on()
                time.sleep(0.5)
                self.buzzer.off()
            except Exception as e:
                print(f"Buzzer error: {e}")
        
        threading.Thread(target=_play, daemon=True).start()

    def cleanup(self):
        if self.buzzer:
            self.buzzer.close()
