import time
try:
    import board
    import busio
    import adafruit_ssd1306
    from PIL import Image, ImageDraw, ImageFont
    HARDWARE_AVAILABLE = True
except ImportError as e:
    HARDWARE_AVAILABLE = False
    print(f"OLED libraries error: {e}. Display will be mocked.")

class DisplayManager:
    def __init__(self, width=128, height=64):
        self.width = width
        self.height = height
        self.enabled = False
        self.oled = None
        self.clear_timer = None
        self.last_student_id = None
        
        if HARDWARE_AVAILABLE:
            try:
                # Create the I2C interface.
                # SCL = GPIO3, SDA = GPIO2
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # Create the SSD1306 OLED class.
                self.oled = adafruit_ssd1306.SSD1306_I2C(self.width, self.height, i2c)
                
                self.enabled = True
                self.clear()
                print("OLED Display initialized successfully.")
            except Exception as e:
                print(f"Warning: OLED Display hardware check failed. Running in mock mode. Error: {e}")
        else:
            print("Warning: OLED dependencies missing. Running in mock mode.")

    def clear(self):
        """Clear display."""
        self.last_student_id = None
        if self.enabled and self.oled:
            try:
                self.oled.fill(0)
                self.oled.show()
            except Exception as e:
                print(f"Error clearing display: {e}")

    def _draw_centered_text(self, draw, text, font, y_pos):
        """Helper to draw centered text."""
        try:
            # Pillow >= 9.2.0 uses textbbox. Older versions might need textsize.
            # Assuming recent Pillow.
            left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
            text_width = right - left
            # text_height = bottom - top
            x_pos = (self.width - text_width) // 2
            draw.text((x_pos, y_pos), text, font=font, fill=255)
        except AttributeError:
             # Fallback for older Pillow
            w, h = draw.textsize(text, font=font)
            x_pos = (self.width - w) // 2
            draw.text((x_pos, y_pos), text, font=font, fill=255)

    def show_attendance(self, name, student_id):
        """Show attendance success message with improved UX."""
        # Cancel any existing timer
        if self.clear_timer:
            self.clear_timer.cancel()

        # Optimization: If same user and display is active (implied by timer existence/recent call),
        # skip redraw and just restart timer.
        if self.last_student_id == student_id:
            # Just restart timer
             from threading import Timer
             self.clear_timer = Timer(3.0, self.clear)
             self.clear_timer.start()
             return

        self.last_student_id = student_id

        if not self.enabled:
            # Mock output to console
            print(f"[OLED MOCK] >> [ {name} | {student_id} ] (Clears in 3s)")
            return

        try:
            # Create blank image for drawing.
            image = Image.new("1", (self.width, self.height))
            draw = ImageDraw.Draw(image)

            # Draw Bounding Box (Border)
            draw.rectangle((0, 0, self.width-1, self.height-1), outline=255, fill=0)

            # Load Fonts
            try:
                font_large = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 15)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 12)
            except IOError:
                font_large = ImageFont.load_default()
                font_small = ImageFont.load_default()

            # Draw Text
            # Layout:
            # Y=5: "Present!" (Small)
            # Y=20: Name (Large)
            # Y=45: ID (Small)
            
            self._draw_centered_text(draw, "Welcome!", font_small, 5)
            self._draw_centered_text(draw, name, font_large, 22)
            self._draw_centered_text(draw, f"ID: {student_id}", font_small, 45)

            # Display image
            self.oled.image(image)
            self.oled.show()
            
            # Auto-clear after 3 seconds
            from threading import Timer
            self.clear_timer = Timer(3.0, self.clear)
            self.clear_timer.start()

        except Exception as e:
            print(f"Error updating display: {e}")
