import time
# # Uncomment the following line to run on Jetson Nano
import RPi.GPIO as GPIO
class PinOut:

    def __init__(self, input_pin: int, relay_pin: int, led_pins: list):
        ''' Initialize the GPIO pins. '''
        self.input_pin = input_pin
        self.relay_pin = relay_pin
        self.led_pins = led_pins
        
        self.status = 'Starting...'
        
        # Uncomment the following lines to run on Jetson Nano
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.input_pin, GPIO.IN) # PIR sensor
        [GPIO.setup(pin, GPIO.OUT) for pin in [*self.led_pins, self.relay_pin]]
        
        self.write_rgb(False, True, False)
        print('PinOut initialized')
        self.write_relay(False)

    def read_pin(self) -> bool:
        ''' Read the value of a pin. '''
        
        return GPIO.input(self.input_pin)
        
    def write_rgb(self, red: bool, green: bool, blue: bool): 
        ''' Write a value to multiple pins. '''
        [GPIO.output(pin, value) for pin, value in zip(self.led_pins, (red, green, blue))]
        
    def write_relay(self, value: bool):
        """ Write a value to a relay pin.

        Args:
            value (bool): The value to write to the relay pin.
        """
        print('Relay value: ', value)
        GPIO.output(self.relay_pin, not value)
            
    def set_sent_status(self):
        """ Set the status to sent and start the timer. """
        self.status = 'sent'
        self.start_time = time.time()
        self.write_rgb(True, True, False)
        self.write_relay(False)

# Mockup for testing on a non-Jetsom Nano device

# class PinOut:
#     def __init__(self, input_pin: int, relay_pin: int, led_pins: list):
#         ''' Initialize the GPIO pins. '''
#         self.input_pin = input_pin
#         self.relay_pin = relay_pin
#         self.led_pins = led_pins
        
#         self.status = 'Starting...'
        
#         # Uncomment the following lines to run on Jetson Nano
        
#         # GPIO.setmode(GPIO.BCM)
#         # GPIO.setwarnings(False)
        
#         # GPIO.setup(self.input_pin, GPIO.IN) # PIR sensor
#         # [GPIO.setup(pin, GPIO.OUT) for pin in [*self.led_pins, self.relay_pin]]
        
#         self.write_rgb(False, True, False)
#         print('PinOut initialized')
#         self.write_relay(False)

#     def read_pin(self) -> bool:
#         ''' Read the value of a pin. '''
        
#         return True
        
#     def write_rgb(self, red: bool, green: bool, blue: bool): 
#         ''' Write a value to multiple pins. '''
#         # [GPIO.output(pin, value) for pin, value in zip(self.led_pins, (red, green, blue))]
#         pass
        
#     def write_relay(self, value: bool):
#         """ Write a value to a relay pin.

#         Args:
#             value (bool): The value to write to the relay pin.
#         """
#         pass
#         # print('Relay value: ', value)
#         # GPIO.output(self.relay_pin, not value)
            
#     def set_sent_status(self):
#         """ Set the status to sent and start the timer. """
#         self.status = 'sent'
#         self.start_time = time.time()
#         self.write_rgb(True, True, False)
#         self.write_relay(False)