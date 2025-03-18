import time
import RPi.GPIO as GPIO
import logging

class LDRSensor:
    def __init__(self):
        """
        Initialize the LDR sensor.
        """
        self.ldr_pin = None
        self.light_pin = None
        self.ldr_threshold = 1000  # Default threshold
        self.logger = logging.getLogger(__name__)
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setwarnings(False)  # Disable GPIO warnings

    def setup(self, ldr_pin, light_pin, threshold):
        """
        Set up the LDR sensor and light pin.
        
        Args:
            ldr_pin (int): GPIO pin number for the LDR sensor.
            light_pin (int): GPIO pin number for the light (e.g., LED).
            threshold (int): Threshold value for light control.
        """
        try:
            self.ldr_pin = ldr_pin
            self.light_pin = light_pin
            self.ldr_threshold = threshold
            GPIO.setup(self.light_pin, GPIO.OUT)
            self.logger.info(f"LDR setup with LDR_PIN: {self.ldr_pin}, LIGHT_PIN: {self.light_pin}, Threshold: {self.ldr_threshold}")
        except Exception as e:
            self.logger.error(f"Failed to setup LDR sensor: {e}")
            raise

    def read_ldr(self):
        """
        Read the LDR sensor value.
        
        Returns:
            int: LDR sensor reading.
        """
        try:
            reading = 0
            GPIO.setup(self.ldr_pin, GPIO.OUT)
            GPIO.output(self.ldr_pin, False)
            time.sleep(0.1)
            GPIO.setup(self.ldr_pin, GPIO.IN)

            while GPIO.input(self.ldr_pin) == GPIO.LOW:
                reading += 1

            self.logger.debug(f"LDR reading: {reading}")
            return reading
        except Exception as e:
            self.logger.error(f"Failed to read LDR sensor: {e}")
            return None

    def control_light(self, duration):
        """
        Control the light based on LDR readings for the specified duration.
        
        Args:
            duration (int): Duration (in seconds) to monitor the LDR sensor.
        """
        try:
            self.logger.info(f"Monitoring LDR for {duration} seconds.")
            start_time = time.time()

            while time.time() - start_time < duration:
                ldr_reading = self.read_ldr()
                if ldr_reading is not None:
                    if ldr_reading < self.ldr_threshold:
                        GPIO.output(self.light_pin, True)
                        self.logger.info(f"LDR reading {ldr_reading} below threshold. Light ON.")
                    else:
                        GPIO.output(self.light_pin, False)
                        self.logger.info(f"LDR reading {ldr_reading} above threshold. Light OFF.")
                time.sleep(1)  # Read every second
        except Exception as e:
            self.logger.error(f"Failed to control light: {e}")
        finally:
            GPIO.output(self.light_pin, False)  # Ensure the light is turned off
            self.logger.info("LDR monitoring completed.")

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        try:
            GPIO.cleanup()
            self.logger.info("GPIO cleanup completed.")
        except Exception as e:
            self.logger.error(f"Failed to cleanup GPIO: {e}")