import json
import paho.mqtt.client as mqtt
import time
import atexit
import threading
import logging
# import RPi.GPIO as GPIO
# from Digital import DigitalIO
# from lcd import LCD
# from steppermotor import StepperMotor
# from Pwm import PWM
# from DHT_11 import DHT11Sensor
# from ultrasonic import UltrasonicSensor
# from PIR import PIRSensor
# from input_handlers import handle_button, handle_keypad
# from ldr import LDRSensor

# Import configurations
from config import MQTT_CONFIG, GPIO_CONFIG

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize components
# digital_io = DigitalIO()
# lcd = LCD()
# stepper_motor = StepperMotor()
# pwm = PWM()


client = mqtt.Client()

# Initialize sensors with MQTT topic from config
# dht11_sensor = DHT11Sensor(client, topic=MQTT_CONFIG["topic"])
# ultrasonic_sensor = UltrasonicSensor(client, topic=MQTT_CONFIG["topic"])
# pir_sensor = PIRSensor(client, topic=MQTT_CONFIG["topic"])
# ldr_sensor = LDRSensor()

# Global flag to control sensor monitoring threads
monitoring_active = True

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker")
        client.subscribe(MQTT_CONFIG["topic"])
    else:
        logger.error(f"Connection failed with code {rc}")

def on_disconnect(client, userdata, rc):
    logger.warning("Disconnected from MQTT broker. Attempting to reconnect...")
    while not client.is_connected():
        try:
            client.reconnect()
            logger.info("Reconnected to MQTT broker")
        except Exception as e:
            logger.error(f"Reconnection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8").strip())
        logger.debug(f"Message received: {data}")
        handle_mqtt_message(data)
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from message payload")
    except Exception as e:
        logger.error(f"Error processing message: {e}")

# Handle MQTT messages
def handle_mqtt_message(data):
    component = data.get('component')
    if not component:
        logger.error("No component specified in message")
        return

    handler = MESSAGE_HANDLERS.get(component)
    if handler:
        handler(data)
    else:
        logger.error(f"No handler found for component: {component}")

# Handlers for different components
def handle_lcd(data):
    msg = data.get('data', {}).get('message')
    if msg:
        # lcd.display_message(msg)
        logger.info(f"LCD message displayed: {msg}")

def handle_digital_io(data):
    component = data.get('component')
    pin = data.get('data', {}).get('pin')
    state = data.get('data', {}).get('state')
    if pin is not None and state is not None:
        # digital_io.switch(component, pin, state)
        logger.info(f"{component} switched to {state} on pin {pin}")

def handle_stepper_motor(data):
    pins = data.get('data', {}).get('pins')
    direction = data.get('data', {}).get('direction')
    steps = data.get('data', {}).get('steps', 400)
    delay = data.get('data', {}).get('delay', 10) / 1000.0
    if pins and direction:
        # GPIO.setup(pins, GPIO.OUT)
        # stepper_motor.move_motor(pins, delay, steps, direction)
        logger.info(f"Stepper motor moving {direction} for {steps} steps with {delay} seconds delay.")

def handle_pwm(data):
    component = data.get('component')
    if component == "light":
        pins = data.get('data', {}).get('pins', [])
        color = data.get('data', {}).get('color', [])
        if pins:
            # pwm.set_rgb_color(pins, color)
            logger.info(f"RGB color set to: {color}")
    elif component == "servo":
        pin = data.get('data', {}).get('pin')
        angle = data.get('data', {}).get('angle')
        if pin is not None and angle is not None:
            # pwm.set_servo_angle(pin, angle)
            logger.info(f"Servo set to angle: {angle} on pin: {pin}")

def handle_dht11(data):
    pin = data['data'].get('pin')
    interval = data['data'].get('interval', 2)  # Default interval
    duration = data['data'].get('duration', 10)  # Default duration
    if pin:
        # dht11_sensor.setup(pin)
        threading.Thread(target=dht11_sensor.read_data, args=(interval, duration), daemon=True).start()
        logger.info(f"DHT11 sensor monitoring started on pin {pin}")

def handle_ultrasonic(data):
    trig_pin = data['data'].get('trig_pin')
    echo_pin = data['data'].get('echo_pin')
    interval = data['data'].get('interval', 1)  # Default interval
    duration = data['data'].get('duration', 10)  # Default duration
    if trig_pin and echo_pin:
        # ultrasonic_sensor.setup(trig_pin, echo_pin)
        # threading.Thread(target=ultrasonic_sensor.monitor, args=(interval, duration), daemon=True).start()
        logger.info(f"Ultrasonic sensor monitoring started on pins {trig_pin} (trig) and {echo_pin} (echo)")

def handle_pir(data):
    pir_pin = data.get('data', {}).get('pin')
    interval = data.get('data', {}).get('interval', 1)  # Default interval
    duration = data.get('data', {}).get('duration', 10)  # Default duration
    if pir_pin:
        # pir_sensor.setup(pir_pin)
        # threading.Thread(target=pir_sensor.monitor, args=(interval, duration), daemon=True).start()
        logger.info(f"PIR sensor monitoring started on pin {pir_pin}")

def handle_ldr(data):
    ldr_pin = data.get('data', {}).get('ldr_pin')
    light_pin = data.get('data', {}).get('light_pin')
    threshold = data.get('data', {}).get('threshold', 1000)
    duration = data.get('data', {}).get('duration', 10)  # Default duration
    if ldr_pin and light_pin:
        # ldr_sensor.setup(ldr_pin, light_pin, threshold)
        # threading.Thread(target=ldr_sensor.control_light, args=(duration,), daemon=True).start()
        logger.info(f"LDR setup on pin {ldr_pin}, controlling light on pin {light_pin}")

def handle_button(data):
    pin = data.get('data', {}).get('pin')
    duration = data.get('data', {}).get('duration', 10)  # Default duration
    if pin:
        threading.Thread(target=handle_button, args=(pin, duration), daemon=True).start()
        logger.info(f"Button handling started on pin {pin}")

def handle_keypad(data):
    pin = data.get('data', {}).get('pin')
    duration = data.get('data', {}).get('duration', 10)  # Default duration
    if pin:
        # threading.Thread(target=handle_keypad, args=(pin, duration), daemon=True).start()
        logger.info(f"Keypad handling started on pin {pin}")

# Dictionary to map components to their handlers
MESSAGE_HANDLERS = {
    "LCD": handle_lcd,
    "led": handle_digital_io,
    "relay": handle_digital_io,
    "buzzer": handle_digital_io,
    "stepper_motor": handle_stepper_motor,
    "light": handle_pwm,
    "servo": handle_pwm,
    "DHT11": handle_dht11,
    "Ultrasonic sensor": handle_ultrasonic,
    "PIR_SENSOR": handle_pir,
    "LDR Sensor": handle_ldr,
    "Button": handle_button,
    "Keypad": handle_keypad,
}

# Register GPIO cleanup on exit
# atexit.register(lambda: GPIO.cleanup())

# MQTT Client Setup
client.username_pw_set(username=MQTT_CONFIG["username"], password=MQTT_CONFIG["password"])
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

# Connect to MQTT broker and loop forever
client.connect(MQTT_CONFIG["broker"], MQTT_CONFIG["port"], 60)
client.loop_start()  # Start the MQTT loop in a separate thread

try:
    logger.info("Listening for MQTT messages...")
    while True:
        time.sleep(0.1)  # Keep the script running
except KeyboardInterrupt:
    logger.info("\nExiting the program.")
finally:
    # Cleanup
    monitoring_active = False
    # digital_io.cleanup()
    # pwm.cleanup()
    # stepper_motor.cleanup()
    # pir_sensor.cleanup()
    client.loop_stop()