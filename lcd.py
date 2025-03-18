# import RPi_I2C_driver

# class LCD:
#     def __init__(self, address=0x20):
#         self.lcd = RPi_I2C_driver.lcd(address)
#         self.lcd.backlight(1)
#         self.lcd.lcd_clear()

#     def display_message(self, msg):
#         self.lcd.lcd_clear()
#         self.lcd.lcd_display_string(msg, 1)

import RPi_I2C_driver
import logging

class LCD:
    def __init__(self, address=0x27):
        """
        Initialize the LCD with a dynamic I2C address.
        
        Args:
            address (int): I2C address of the LCD. Default is 0x27.
        """
        try:
            self.lcd = RPi_I2C_driver.lcd(address)
            self.lcd.backlight(1)  # Turn on the backlight
            self.lcd.lcd_clear()   # Clear the display
            self.logger = logging.getLogger(__name__)
            self.logger.info(f"LCD initialized with address 0x{address:02X}")
        except Exception as e:
            self.logger.error(f"Failed to initialize LCD with address 0x{address:02X}: {e}")
            raise

    def display_message(self, msg):
        """
        Display a message on the LCD. If the message is longer than 16 characters,
        it will be split into two lines.
        
        Args:
            msg (str): Message to display on the LCD.
        """
        try:
            self.lcd.lcd_clear()  # Clear the display before showing a new message

            # Split the message into two lines if it exceeds 16 characters
            if len(msg) <= 16:
                self.lcd.lcd_display_string(msg, 1)  # Display on line 1
            else:
                line1 = msg[:16]  # First 16 characters
                line2 = msg[16:32]  # Next 16 characters (if available)
                self.lcd.lcd_display_string(line1, 1)  # Display on line 1
                self.lcd.lcd_display_string(line2, 2)  # Display on line 2

            self.logger.info(f"Displayed message on LCD: {msg}")
        except Exception as e:
            self.logger.error(f"Failed to display message on LCD: {e}")