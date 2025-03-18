import json
import paho.mqtt.client as mqtt
import time
import atexit
import RPi.GPIO as GPIO
from Digital import DigitalIO
from lcd import LCD
from steppermotor import StepperMotor
from Pwm import PWM
from DHT_11 import DHT11Sensor  
from ultrasonic import UltrasonicSensor
from PIR import PIRSensor
from input_handlers import handle_button, handle_keypad  # Import button and keypad handlers
from ldr import LDRSensor

# MQTT Broker Configuration
broker = 'iiotif.com'
port = 1883
username = 'blitz_server'
password = 'sdsmakapgnjvngrp@!#@snsdfod'
topic = "a/sampleAsset_1718789748945"

# Initialize components
digital_io = DigitalIO()
lcd = LCD()
stepper_motor = StepperMotor()
pwm = PWM()
client = mqtt.Client()

# Initialize Sensor
dht11_sensor = DHT11Sensor(client)
ultrasonic_sensor = UltrasonicSensor(client)
pir_sensor = PIRSensor(client, topic)
ldr_sensor = LDRSensor() 

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker")
    client.subscribe(topic)

def on_message(client, userdata, message):
    try:
        data = json.loads(message.payload.decode("utf-8").strip())
        component = data.get('component')

        print(f"Message received: {data}")  # Debugging print

        if component == 'LCD':
            msg = data.get('data', {}).get('message')
            if msg:
                lcd.display_message(msg)
                print(f"LCD message displayed: {msg}")  # Debugging print

        elif component in ["led", "relay", "buzzer"]:
            digital_io.switch(component, data.get('data', {}))

        elif component == 'stepper_motor':
            pins = data.get('data', {}).get('pins')
            direction = data.get('data', {}).get('direction')
            steps = data.get('data', {}).get('steps', 400)
            delay = data.get('data', {}).get('delay', 10) / 1000.0
            
            if pins and direction:
                GPIO.setup(pins, GPIO.OUT)
                stepper_motor.move_motor(pins, delay, steps, direction)
                print(f"Stepper motor moving {direction} for {steps} steps with {delay} seconds delay.")  # Debugging print

        elif component == "light":
            pins = data.get('data', {}).get('pins', [])
            color = data.get('data', {}).get('color', [])
            if pins:
                pwm.set_rgb_color(pins, color)
                print(f"RGB color set to: {color}")  # Debugging print

        elif component == "servo":
            pin = data.get('data', {}).get('pin')
            angle = data.get('data', {}).get('angle')
            if pin is not None and angle is not None:
                pwm.set_servo_angle(pin, angle)
                print(f"Servo set to angle: {angle} on pin: {pin}")  # Debugging print

        elif component == "DHT11":
            pin = data['data'].get('pin')
            interval = data['data'].get('interval')  # Default interval
            duration = data['data'].get('duration')  # Default duration
            
            # Setup the DHT11 sensor and read data
            dht11_sensor.setup(pin)
            dht11_sensor.read_data(interval, duration)

        elif component == "Ultrasonic sensor":
            trig_pin = data['data'].get('trig_pin')
            echo_pin = data['data'].get('echo_pin')
            interval = data['data'].get('interval')  # Default interval
            duration = data['data'].get('duration')  # Default duration

            
            # Setup the Ultrasonic sensor
            ultrasonic_sensor.setup(trig_pin, echo_pin)
            ultrasonic_sensor.monitor(interval, duration)

        elif component == "PIR_SENSOR":
            pir_pin = data.get('data', {}).get('pin')
            interval = data.get('data', {}).get('interval')  # Default interval
            duration = data.get('data', {}).get('duration')  # Default duration
            if pir_pin is not None:
                pir_sensor.setup(pir_pin)
                pir_sensor.monitor(interval, duration)

                # Handle LDR component
        elif component == "LDR Sensor":
            ldr_pin = data.get('data', {}).get('ldr_pin')
            light_pin = data.get('data', {}).get('light_pin')
            threshold = data.get('data', {}).get('threshold', 1000)
            duration = data.get('data', {}).get('duration', 10)  # Default duration 10 seconds
            if ldr_pin is not None and light_pin is not None:
                ldr_sensor.setup(ldr_pin, light_pin, threshold)
                ldr_sensor.control_light(duration)
                print(f"LDR setup on pin {ldr_pin}, controlling light on pin {light_pin}, threshold: {threshold}, duration: {duration}")

        # Handle Button
        elif component == "Button":
            pin = data.get('data', {}).get('pin')  # Get pin for the button
            duration = data.get('data', {}).get('duration')  # Default duration 10 seconds
            if pin is not None:
                handle_button(pin, duration)
                print(f"Handling button on pin: {pin} for {duration} seconds")
                

        # Handle Keypad
        elif component == "Keypad":
            pin = data.get('data', {}).get('pin')  # Get pin for the keypad
            duration = data.get('data', {}).get('duration')  # Default duration 10 seconds
            if pin is not None:
                handle_keypad(pin, duration)
                print(f"Handling keypad on pin: {pin} for {duration} seconds")

    except json.JSONDecodeError:
        print("Failed to decode JSON from message payload")
    except Exception as e:
        print(f"Error processing message: {e}")

# Register GPIO cleanup on exit
atexit.register(lambda: GPIO.cleanup())

# MQTT Client Setup
client.username_pw_set(username=username, password=password)
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT broker and loop forever
client.connect(broker, port, 60)
client.loop_start()  # Start the MQTT loop in a separate thread

try:
    print("Listening for MQTT messages...")
    while True:
        time.sleep(1)  # Keep the script running
except KeyboardInterrupt:
    print("\nExiting the program.")
finally:
    # Cleanup
    digital_io.cleanup()
    pwm.cleanup()
    stepper_motor.cleanup()
    pir_sensor.cleanup()  # Cleanup PIR sensor
    client.loop_stop()
