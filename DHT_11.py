# import RPi.GPIO as GPIO
# from dht11 import DHT11
import time
import random
import paho.mqtt.client as mqtt
import json
import logging

class DHT11Sensor:
    def __init__(self, client: mqtt.Client, topic: str):
        """
        Initialize the DHT11 sensor with an MQTT client and topic.
        
        Args:
            client (mqtt.Client): MQTT client for publishing sensor data.
            topic (str): MQTT topic to publish sensor data to.
        """
        self.client = client
        self.topic = topic  # Store the MQTT topic
        self.sensor = None
        self.logger = logging.getLogger(__name__)
        self.monitoring_active = False  # Flag to control monitoring loop

    def setup(self, pin):
        """
        Set up the DHT11 sensor on the specified GPIO pin.
        
        Args:
            pin (int): GPIO pin number where the DHT11 sensor is connected.
        """
        try:
            # self.sensor = DHT11(pin=pin)
            self.logger.info(f"DHT11 sensor setup on pin {pin}")
        except Exception as e:
            self.logger.error(f"Failed to setup DHT11 sensor on pin {pin}: {e}")
            raise

    def read_data(self, interval=2, duration=10):
        """
        Read data from the DHT11 sensor and publish it to MQTT.
        
        Args:
            interval (int): Time interval (in seconds) between readings. Default is 2 seconds.
            duration (int): Total duration (in seconds) to monitor the sensor. Default is 10 seconds.
        """
        # if not self.sensor:
        #     self.logger.error("DHT11 sensor not setup. Call setup() first.")
        #     return

        self.monitoring_active = True
        start_time = time.time()

        while self.monitoring_active and (time.time() - start_time < duration):
            try:
                humidity = round(random.uniform(70, 90), 2)
                temperature = round(random.uniform(20, 35), 2)
                self.publish_sensor_data(temperature, humidity)
                # result = self.sensor.read()
                # if result.is_valid():
                #     humidity = round(random.uniform(70, 90), 2)
                #     temperature = round(random.uniform(20, 35), 2)
                #     humidity = round(result.humidity, 2)
                #     temperature = round(result.temperature, 2)
                #     self.publish_sensor_data(temperature, humidity)
                # else:
                #     self.logger.warning(f"Invalid DHT11 sensor reading. Error code: {result.error_code}")
            except Exception as e:
                self.logger.error(f"Error reading DHT11 sensor: {e}")
            time.sleep(interval)

        self.logger.info("DHT11 sensor monitoring completed.")

    def publish_sensor_data(self, temperature, humidity):
        """
        Publish temperature and humidity data to the MQTT broker.
        
        Args:
            temperature (float): Temperature reading in °C.
            humidity (float): Humidity reading in %.
        """
        try:
            payload = {
                "temperature": temperature,
                "humidity": humidity
            }
            self.client.publish(self.topic, json.dumps(payload))  # Use self.topic
            self.logger.info(f"Published to {self.topic}: Temperature: {temperature} °C, Humidity: {humidity} %")
        except Exception as e:
            self.logger.error(f"Failed to publish sensor data: {e}")

    def stop_monitoring(self):
        """
        Stop the monitoring loop for the DHT11 sensor.
        """
        self.monitoring_active = False
        self.logger.info("DHT11 sensor monitoring stopped.")