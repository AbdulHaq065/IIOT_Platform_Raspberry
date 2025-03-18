import RPi.GPIO as GPIO
import time
import logging

class StepperMotor:
    def __init__(self):
        """
        Initialize the stepper motor.
        """
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setwarnings(False)  # Disable GPIO warnings
        self.logger = logging.getLogger(__name__)

    def set_step(self, pins, step_sequence):
        """
        Set the GPIO pins to the specified step sequence.
        
        Args:
            pins (list): List of GPIO pins connected to the stepper motor.
            step_sequence (list): List of states for each pin in the step sequence.
        """
        try:
            for pin, state in zip(pins, step_sequence):
                GPIO.output(pin, state)
            self.logger.debug(f"Set step sequence: {step_sequence} on pins {pins}")
        except Exception as e:
            self.logger.error(f"Failed to set step sequence: {e}")

    def move_motor(self, pins, delay, steps, direction):
        """
        Move the stepper motor in the specified direction.
        
        Args:
            pins (list): List of GPIO pins connected to the stepper motor.
            delay (float): Delay (in seconds) between steps.
            steps (int): Number of steps to move.
            direction (str): Direction of movement ('clockwise' or 'counterclockwise').
        """
        try:
            step_sequence = [
                [1, 0, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 0, 1],
                [1, 0, 0, 1]
            ] if direction == 'clockwise' else [
                [1, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 1, 0],
                [1, 0, 1, 0]
            ]

            self.logger.info(f"Moving stepper motor {direction} for {steps} steps with {delay} seconds delay.")

            for _ in range(steps):
                for step in step_sequence:
                    self.set_step(pins, step)
                    time.sleep(delay)
        except Exception as e:
            self.logger.error(f"Failed to move stepper motor: {e}")

    def cleanup(self):
        """
        Clean up GPIO resources.
        """
        try:
            GPIO.cleanup()
            self.logger.info("GPIO cleanup completed.")
        except Exception as e:
            self.logger.error(f"Failed to cleanup GPIO: {e}")