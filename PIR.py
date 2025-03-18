import threading
import time
import RPi.GPIO as GPIO
import json
import logging

class PIRSensor:
    def __init__(self, client, topic):
        """
        Initialize the PIR sensor with an MQTT client and topic.
        
        Args:
            client: MQTT client for publishing sensor data.
            topic: MQTT topic to publish sensor data to.
        """
        self.client = client
        self.topic = topic
        self.pin = None
        self.monitor_thread = None
        self.stop_thread = False
        self.logger = logging.getLogger(__name__)

    def setup(self, pin):
        """
        Set up the PIR sensor on the specified GPIO pin.
        
        Args:
            pin (int): GPIO pin number where the PIR sensor is connected.
        """
        try:
            self.pin = pin
            GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
            GPIO.setup(self.pin, GPIO.IN)
            self.logger.info(f"PIR sensor setup on pin {pin}")
        except Exception as e:
            self.logger.error(f"Failed to setup PIR sensor on pin {pin}: {e}")
            raise

    def monitor(self, interval=1, duration=10):
        """
        Monitor the PIR sensor and publish data for the given duration.
        
        Args:
            interval (int): Time interval (in seconds) between readings. Default is 1 second.
            duration (int): Total duration (in seconds) to monitor the sensor. Default is 10 seconds.
        """
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.stop_thread = True  # Stop the existing monitoring thread
            self.monitor_thread.join()  # Wait for the thread to finish

        self.stop_thread = False
        self.monitor_thread = threading.Thread(target=self.run, args=(interval, duration))
        self.monitor_thread.start()
        self.logger.info(f"PIR sensor monitoring started on pin {self.pin}")

    def run(self, interval, duration):
        """
        Internal method to monitor the PIR sensor and publish data.
        
        Args:
            interval (int): Time interval (in seconds) between readings.
            duration (int): Total duration (in seconds) to monitor the sensor.
        """
        start_time = time.time()
        last_state = None

        while not self.stop_thread and (time.time() - start_time) < duration:
            try:
                motion_detected = GPIO.input(self.pin) == GPIO.HIGH

                # Publish message only if there is a change in state
                if motion_detected != last_state:
                    last_state = motion_detected
                    message = "Motion Detected" if motion_detected else "No Motion Detected"

                    # Prepare and publish the MQTT message
                    payload = {
                        "component": "PIR_SENSOR",
                        "data": {
                            "pin": self.pin,
                            "message": message,
                            "interval": interval,
                            "duration": duration
                        }
                    }
                    self.client.publish(self.topic, json.dumps(payload))
                    self.logger.info(f"Published: {message} on pin {self.pin}")

                time.sleep(interval)  # Wait for the specified interval before checking again
            except Exception as e:
                self.logger.error(f"Error monitoring PIR sensor: {e}")
                break

        self.logger.info("PIR sensor monitoring completed.")

    def cleanup(self):
        """
        Clean up resources and stop the monitoring thread.
        """
        self.stop_thread = True
        if self.monitor_thread is not None and self.monitor_thread.is_alive():
            self.monitor_thread.join()  # Wait for the thread to finish
        GPIO.cleanup(self.pin)
        self.logger.info("PIR sensor cleanup completed.")