import RPi.GPIO as GPIO
import json
import logging

class PWM:
    def __init__(self):
        """
        Initialize the PWM class.
        """
        self.pwm_instances = {}  # Dictionary to store PWM instances
        self.logger = logging.getLogger(__name__)
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

    def setup_pwm(self, pin):
        """
        Set up PWM on the specified GPIO pin.
        
        Args:
            pin (int): GPIO pin number to set up PWM.
        """
        try:
            if pin not in self.pwm_instances:
                GPIO.setup(pin, GPIO.OUT)
                pwm = GPIO.PWM(pin, 1000)  # 1 kHz frequency
                pwm.start(0)
                self.pwm_instances[pin] = pwm
                self.logger.info(f"PWM setup on pin {pin}")
        except Exception as e:
            self.logger.error(f"Failed to setup PWM on pin {pin}: {e}")
            raise

    def set_duty_cycle(self, pin, duty_cycle):
        """
        Set the duty cycle for the specified PWM pin.
        
        Args:
            pin (int): GPIO pin number.
            duty_cycle (float): Duty cycle (0 to 100).
        """
        try:
            self.setup_pwm(pin)
            self.pwm_instances[pin].ChangeDutyCycle(duty_cycle)
            self.logger.debug(f"Set duty cycle to {duty_cycle}% on pin {pin}")
        except Exception as e:
            self.logger.error(f"Failed to set duty cycle on pin {pin}: {e}")

    def set_rgb_color(self, pins, color):
        """
        Set the RGB color using PWM.
        
        Args:
            pins (list): List of GPIO pins for R, G, and B.
            color (list): List of duty cycles for R, G, and B (0 to 100).
        """
        try:
            for pin, value in zip(pins, color):
                self.set_duty_cycle(pin, value)
            self.logger.info(f"RGB set to R={color[0]}%, G={color[1]}%, B={color[2]}%")
        except Exception as e:
            self.logger.error(f"Failed to set RGB color: {e}")

    def set_servo_angle(self, pin, angle):
        """
        Set the servo angle using PWM.
        
        Args:
            pin (int): GPIO pin number.
            angle (int): Servo angle (0, 90, or 180 degrees).
        """
        try:
            duty_cycle = {0: 2.5, 90: 7.5, 180: 12.5}.get(angle)
            if duty_cycle is not None:
                self.set_duty_cycle(pin, duty_cycle)
                self.logger.info(f"Servo set to {angle} degrees on pin {pin}")
            else:
                self.logger.error(f"Invalid servo angle: {angle}")
        except Exception as e:
            self.logger.error(f"Failed to set servo angle on pin {pin}: {e}")

    def cleanup(self):
        """
        Clean up PWM instances and GPIO resources.
        """
        try:
            for pin, pwm_instance in self.pwm_instances.items():
                pwm_instance.stop()
                self.logger.info(f"Stopped PWM on pin {pin}")
            GPIO.cleanup()
            self.logger.info("PWM cleanup completed.")
        except Exception as e:
            self.logger.error(f"Failed to cleanup PWM: {e}")