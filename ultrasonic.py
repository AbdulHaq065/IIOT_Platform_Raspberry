# # UltrasonicSensor.py
# import RPi.GPIO as GPIO
# import time
# import paho.mqtt.client as mqtt
# import json

# class UltrasonicSensor:
#     def __init__(self, client: mqtt.Client):
#         self.client = client
#         self.trig_pin = None
#         self.echo_pin = None
#         self.interval = 1  # Default interval
#         self.threshold_dist = 100  # Default threshold in cm
    
#     def setup(self, trig_pin, echo_pin):
#         """Setup the ultrasonic sensor pins."""
#         self.trig_pin = trig_pin
#         self.echo_pin = echo_pin
        
#         GPIO.setmode(GPIO.BCM)
#         GPIO.setup(self.trig_pin, GPIO.OUT)
#         GPIO.setup(self.echo_pin, GPIO.IN)

#     def distance(self):
#         """Measure distance using the ultrasonic sensor."""
#         GPIO.output(self.trig_pin, True)
#         time.sleep(0.00001)
#         GPIO.output(self.trig_pin, False)

#         pulse_start = time.time()
#         while GPIO.input(self.echo_pin) == 0:
#             pulse_start = time.time()

#         pulse_end = time.time()
#         while GPIO.input(self.echo_pin) == 1:
#             pulse_end = time.time()

#         pulse_duration = pulse_end - pulse_start
#         distance = pulse_duration * 17150
#         return round(distance, 2)

#     def publish_distance(self):
#         """Publish the measured distance to MQTT."""
#         dist = self.distance()
#         payload = {
#             "component": "Ultrasonic sensor",
#             "data": {
#                 "distance": dist
#             }
#         }
#         self.client.publish("a/sampleAsset_1718789748945", json.dumps(payload))
#         print(f"Published distance: {dist} cm")

#     def monitor(self, interval, duration):
#         """Monitor the ultrasonic sensor and publish data for the given duration."""
#         start_time = time.time()
#         while time.time() - start_time < duration:
#             self.publish_distance()
#             if self.distance() <= self.threshold_dist:
#                 print("MOTION DETECTED")
#             else:
#                 print("Area clear. No object within threshold.")
#             time.sleep(interval)

#     def set_threshold(self, threshold):
#         """Set a new threshold distance."""
#         self.threshold_dist = threshold


# import RPi.GPIO as GPIO
import time
import random
import paho.mqtt.client as mqtt
import json
import logging

class UltrasonicSensor:
    def __init__(self, client: mqtt.Client, topic: str):
        """
        Initialize the ultrasonic sensor with an MQTT client and topic.
        
        Args:
            client (mqtt.Client): MQTT client for publishing sensor data.
            topic (str): MQTT topic to publish sensor data to.
        """
        self.client = client
        self.topic = topic  # Store the MQTT topic
        self.trig_pin = None
        self.echo_pin = None
        self.monitoring_active = False  # Flag to control monitoring loop
        self.logger = logging.getLogger(__name__)

    def setup(self, trig_pin, echo_pin):
        """
        Set up the ultrasonic sensor on the specified GPIO pins.
        
        Args:
            trig_pin (int): GPIO pin number for the trigger pin.
            echo_pin (int): GPIO pin number for the echo pin.
        """
        try:
            self.trig_pin = trig_pin
            self.echo_pin = echo_pin

            # GPIO.setmode(GPIO.BCM)
            # GPIO.setup(self.trig_pin, GPIO.OUT)
            # GPIO.setup(self.echo_pin, GPIO.IN)
            self.logger.info(f"Ultrasonic sensor setup on trig_pin {trig_pin} and echo_pin {echo_pin}")
        except Exception as e:
            self.logger.error(f"Failed to setup ultrasonic sensor: {e}")
            raise

    def distance(self):
        """
        Measure distance using the ultrasonic sensor.
        
        Returns:
            float: Distance in centimeters.
        """
        try:
            GPIO.output(self.trig_pin, True)
            time.sleep(0.00001)
            GPIO.output(self.trig_pin, False)

            pulse_start = time.time()
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()

            pulse_end = time.time()
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()

            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound in cm/s
            return round(distance, 2)
        except Exception as e:
            self.logger.error(f"Error measuring distance: {e}")
            return None

    def publish_distance(self):
        """
        Publish the measured distance to the MQTT broker.
        """
        try:
            # dist = self.distance()
            dist = round(random.uniform(10, 200), 2)
            if dist is not None:
                payload = {
                    "component": "Ultrasonic sensor",
                    "data": {
                        "distance": dist
                    }
                }
                self.client.publish(self.topic, json.dumps(payload))
                self.logger.info(f"Published distance: {dist} cm")
            else:
                self.logger.warning("Failed to measure distance. Skipping publish.")
        except Exception as e:
            self.logger.error(f"Failed to publish distance: {e}")

    def monitor(self, interval=1, duration=10):
        """
        Monitor the ultrasonic sensor and publish data for the given duration.
        
        Args:
            interval (int): Time interval (in seconds) between readings. Default is 1 second.
            duration (int): Total duration (in seconds) to monitor the sensor. Default is 10 seconds.
        """
        if not self.trig_pin or not self.echo_pin:
            self.logger.error("Ultrasonic sensor not setup. Call setup() first.")
            return

        self.monitoring_active = True
        start_time = time.time()

        while self.monitoring_active and (time.time() - start_time < duration):
            self.publish_distance()
            time.sleep(interval)

        self.logger.info("Ultrasonic sensor monitoring completed.")

    def stop_monitoring(self):
        """
        Stop the monitoring loop for the ultrasonic sensor.
        """
        self.monitoring_active = False
        self.logger.info("Ultrasonic sensor monitoring stopped.")