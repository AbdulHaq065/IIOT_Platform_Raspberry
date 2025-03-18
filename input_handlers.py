# import paho.mqtt.client as mqtt
# import RPi.GPIO as GPIO
# import time
# import json
# from keypad import keypad  # Import the keypad class to detect key presses

# # GPIO setup
# GPIO.setmode(GPIO.BCM)

# ROW_PINS = [2, 3, 4, 5]  # Example GPIO pins for the rows
# COL_PINS = [6, 7, 8, 9]     # Example GPIO pins for the columns

# # Function to handle button logic
# def handle_button(pin, duration):
#     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup the button pin
#     last_state = GPIO.input(pin)
    
#     start_time = time.time()
#     while time.time() - start_time < duration:
#         current_state = GPIO.input(pin)
#         if current_state == GPIO.LOW and last_state == GPIO.HIGH:  # Button pressed
#             publish_message(pin, True)  # Send pressed event
#             time.sleep(0.2)  # Debounce delay
#         elif current_state == GPIO.HIGH and last_state == GPIO.LOW:  # Button released
#             publish_message(pin, False)  # Send released event
#             time.sleep(0.2)  # Debounce delay
#         last_state = current_state
#         time.sleep(0.1)  # Polling delay

# # Function to handle keypad logic
# def handle_keypad(duration):
#     kp = keypad(ROW_PINS, COL_PINS)  # Initialize Keypad with row and column pins
    
#     print(f"Handling keypad for {duration} seconds")

#     start_time = time.time()
#     while time.time() - start_time < duration:
#         key = kp.getKey()  # Get the pressed key

#         if key is not None:  # If a key was pressed
#             print(f"Key pressed: {key}")
#             publish_key_event(key)  # Publish the keypress event
#             time.sleep(0.2)  # Debounce delay
#         time.sleep(0.1)  # Polling delay

# def publish_message(pin, pressed_state):
#     payload = {
#         "component": "Button",
#         "data": {
#             "pin": pin,
#             "pressed": pressed_state,
#             "duration": duration
#         }
#     }
#     client.publish(topic, json.dumps(payload))
#     print(f"Button on pin {pin} {'pressed' if pressed_state else 'released'}, message published")

# def publish_key_event(key):
#     payload = {
#         "component": "Keypad",
#         "data": {
#             "key": key,  # Send the pressed key in the payload
#             "duration": duration
#         }
#     }
#     client.publish(topic, json.dumps(payload))
#     print(f"Key '{key}' pressed, message published")

# # Main function to run the logic
# def main():
#     # Example duration (in seconds)
#     global duration
#     duration = 10  # Set duration for both button and keypad handling

#     # Get button pin from MQTT
#     button_pin = int(input("Enter button pin: "))  # Modify to receive from MQTT if needed
#     print(f"Listening for button presses on pin: {button_pin} for {duration} seconds")

#     try:
#         handle_button(button_pin, duration)  # Start handling button presses
#         handle_keypad(duration)  # Start handling keypad presses
#     except KeyboardInterrupt:
#         print("\nExiting the program.")
#     finally:
#         GPIO.cleanup()  # Clean up GPIO settings
#         client.loop_stop()  # Stop the MQTT loop

# if __name__ == "__main__":
#     main()

import RPi.GPIO as GPIO
import time
import json
import logging
from keypad import keypad  # Import the keypad class to detect key presses

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings

# Example GPIO pins for the rows and columns of the keypad
ROW_PINS = [2, 3, 4, 5]  # Replace with your GPIO pin numbers
COL_PINS = [6, 7, 8, 9]  # Replace with your GPIO pin numbers

# Function to handle button logic
def handle_button(client, topic, pin, duration):
    """
    Handle button presses and publish events to MQTT.
    
    Args:
        client (mqtt.Client): MQTT client for publishing events.
        topic (str): MQTT topic to publish events to.
        pin (int): GPIO pin number for the button.
        duration (int): Duration (in seconds) to monitor the button.
    """
    try:
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Setup the button pin
        last_state = GPIO.input(pin)
        logger.info(f"Listening for button presses on pin {pin} for {duration} seconds")

        start_time = time.time()
        while time.time() - start_time < duration:
            current_state = GPIO.input(pin)
            if current_state == GPIO.LOW and last_state == GPIO.HIGH:  # Button pressed
                publish_message(client, topic, pin, True)  # Send pressed event
                time.sleep(0.2)  # Debounce delay
            elif current_state == GPIO.HIGH and last_state == GPIO.LOW:  # Button released
                publish_message(client, topic, pin, False)  # Send released event
                time.sleep(0.2)  # Debounce delay
            last_state = current_state
            time.sleep(0.1)  # Polling delay
    except Exception as e:
        logger.error(f"Failed to handle button on pin {pin}: {e}")

# Function to handle keypad logic
def handle_keypad(client, topic, duration):
    """
    Handle keypad presses and publish events to MQTT.
    
    Args:
        client (mqtt.Client): MQTT client for publishing events.
        topic (str): MQTT topic to publish events to.
        duration (int): Duration (in seconds) to monitor the keypad.
    """
    try:
        kp = keypad(ROW_PINS, COL_PINS)  # Initialize Keypad with row and column pins
        logger.info(f"Handling keypad for {duration} seconds")

        start_time = time.time()
        while time.time() - start_time < duration:
            key = kp.getKey()  # Get the pressed key

            if key is not None:  # If a key was pressed
                logger.info(f"Key pressed: {key}")
                publish_key_event(client, topic, key)  # Publish the keypress event
                time.sleep(0.2)  # Debounce delay
            time.sleep(0.1)  # Polling delay
    except Exception as e:
        logger.error(f"Failed to handle keypad: {e}")

def publish_message(client, topic, pin, pressed_state):
    """
    Publish button press/release events to MQTT.
    
    Args:
        client (mqtt.Client): MQTT client for publishing events.
        topic (str): MQTT topic to publish events to.
        pin (int): GPIO pin number for the button.
        pressed_state (bool): True if pressed, False if released.
    """
    try:
        payload = {
            "component": "Button",
            "data": {
                "pin": pin,
                "pressed": pressed_state
            }
        }
        client.publish(topic, json.dumps(payload))
        logger.info(f"Button on pin {pin} {'pressed' if pressed_state else 'released'}, message published")
    except Exception as e:
        logger.error(f"Failed to publish button event: {e}")

def publish_key_event(client, topic, key):
    """
    Publish keypad keypress events to MQTT.
    
    Args:
        client (mqtt.Client): MQTT client for publishing events.
        topic (str): MQTT topic to publish events to.
        key (str): The key that was pressed.
    """
    try:
        payload = {
            "component": "Keypad",
            "data": {
                "key": key  # Send the pressed key in the payload
            }
        }
        client.publish(topic, json.dumps(payload))
        logger.info(f"Key '{key}' pressed, message published")
    except Exception as e:
        logger.error(f"Failed to publish key event: {e}")