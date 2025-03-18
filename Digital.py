import RPi.GPIO as GPIO
import json
import logging

class DigitalIO:
    def __init__(self):
        """
        Initialize the DigitalIO class.
        """
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.logger = logging.getLogger(__name__)

    def switch(self, component, data):
        """
        Control a digital component (e.g., LED, relay, buzzer).
        
        Args:
            component (str): Type of component ('led', 'relay', 'buzzer').
            data (dict): Dictionary containing 'pin' and 'state' keys.
        """
        try:
            pin = data.get('pin')
            state = data.get('state')

            if pin is None or state is None:
                self.logger.error(f"Invalid data for {component}: {data}")
                return

            GPIO.setup(pin, GPIO.OUT)

            if component in ['led', 'relay', 'buzzer']:
                GPIO.output(pin, GPIO.HIGH if state == "ON" else GPIO.LOW)
                self.logger.info(f"{component.capitalize()} is {'ON' if state == 'ON' else 'OFF'} on pin {pin}")
            else:
                self.logger.error(f"Unknown digital component: {component}")
        except Exception as e:
            self.logger.error(f"Failed to control {component} on pin {pin}: {e}")

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        try:
            GPIO.cleanup()
            self.logger.info("GPIO cleanup completed.")
        except Exception as e:
            self.logger.error(f"Failed to cleanup GPIO: {e}")