# import paho.mqtt.client as mqtt
# import json
# import time
# import random

# # MQTT Broker Configuration
# broker = 'iiotif.com'
# port = 1883
# username = 'blitz_server'
# password = 'sdsmakapgnjvngrp@!#@snsdfod'
# topic = "a/sampleAsset_1718789748945"

# # MQTT Client Setup
# client = mqtt.Client()
# client.username_pw_set(username, password)

# # Connect to MQTT Broker
# client.connect(broker, port, 60)
# client.loop_start()  # Start the loop in a separate thread

# # Continuous Publishing Loop
# while True:
#     messages = [
#         {"component": "light", "data": {"pins": [12, 11, 13], "color": [random.randint(0, 255) for _ in range(3)]}},
#         {"component": "Ultrasonic sensor", "data": {"trig_pin": 15, "echo_pin": 14, "interval": random.randint(1, 10), "duration": random.randint(10, 30)}},
#         {"component": "stepper_motor", "data": {"pins": [16, 19, 20, 21], "direction": random.choice(["clockwise", "counterclockwise"]), "steps": random.randint(100, 500), "delay": random.randint(1, 10)}},
#         {"component": "led", "data": {"pin": 11, "state": random.choice(["ON", "OFF"])}},
#         {"component": "buzzer", "data": {"pin": 22, "state": random.choice(["ON", "OFF"])}},
#         {"component": "relay", "data": {"pin": 26, "state": random.choice(["ON", "OFF"])}},
#         {"component": "SERVO", "data": {"pin": 24, "angle": random.randint(0, 180)}},
#         {"component": "DHT11", "data": {"pin": 4, "interval": random.randint(2, 10), "duration": random.randint(5, 15)}},
#         {"component": "PIR", "data": {"pin": 21, "interval": random.randint(1, 5), "duration": random.randint(20, 40)}},
#         {"component": "Button", "data": {"pins": [6, 7], "duration": random.randint(5, 15)}},
#         {"component": "LCD", "data": {"message": random.choice(["Hello, World!", "Temperature: 25°C", "Motion Detected!", "System Active"])}},
#         {"component": "Keypad", "data": {"key": random.choice(["A", "B", "C", "D", "1", "2", "3", "4"])}},
#         {"component": "LDR Sensor", "data": {"ldr_pin": 25, "light_pin": 10, "threshold": random.randint(10, 100)}}
#     ]

#     # Sending messages one by one
#     for message in messages:
#         payload = json.dumps(message)
#         print(f"[DEBUG] Publishing: {payload}")  # Debugging Output
#         client.publish(topic, payload)
#         time.sleep(0.2)  # Delay before sending the next message

# # client.loop_stop()  # Uncomment if stopping the script
# # client.disconnect()  # Uncomment if stopping the script


from config import MQTT_CONFIG
from DHT_11 import DHT11Sensor
from ultrasonic import UltrasonicSensor
import paho.mqtt.client as mqtt
import logging
import time
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MQTT client
client = mqtt.Client()
client.username_pw_set(username=MQTT_CONFIG["username"], password=MQTT_CONFIG["password"])
client.connect(MQTT_CONFIG["broker"], MQTT_CONFIG["port"])

# Initialize ultrasonic sensor with the topic from config
ultrasonic_sensor = UltrasonicSensor(client, topic=MQTT_CONFIG["topic"])
ultrasonic_sensor.setup(trig_pin=23, echo_pin=24)  # Replace with your GPIO pin numbers

# Initialize DHT11 sensor with the topic from config
dht11_sensor = DHT11Sensor(client, topic=MQTT_CONFIG["topic"])
dht11_sensor.setup(pin=14)  # Replace 14 with your GPIO pin number

# Start monitoring for DHT11 sensor in a separate thread
dht11_thread = threading.Thread(
    target=dht11_sensor.read_data,
    kwargs={"interval": 2, "duration": 30}  # Monitor for 30 seconds with 2-second intervals
)

# Start monitoring for ultrasonic sensor in a separate thread
ultrasonic_thread = threading.Thread(
    target=ultrasonic_sensor.monitor,
    kwargs={"interval": 5, "duration": 20}  # Monitor for 20 seconds with 5-second intervals
)

# Start both threads
dht11_thread.start()
ultrasonic_thread.start()

# Keep the main program running
try:
    while dht11_thread.is_alive() or ultrasonic_thread.is_alive():
        time.sleep(1)
except KeyboardInterrupt:
    logger.info("Stopping sensor monitoring...")
    dht11_sensor.stop_monitoring()
    ultrasonic_sensor.stop_monitoring()
    dht11_thread.join()
    ultrasonic_thread.join()
    logger.info("Program stopped.")