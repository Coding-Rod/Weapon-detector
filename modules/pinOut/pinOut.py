import time
try:
    import RPi.GPIO as GPIO
except ModuleNotFoundError:
    print('Mocking GPIO')
    from .gpio_mock import GPIO
class PinOut:
    _status = None

    STATUS_COLORS = {
        'starting': (False, True, False),
        'standby': (False, False, True),
        'running': (False, True, True),
        'sent': (True, False, True),
        'alarm': (True, False, False),
        'password': (False, False, True),
        'learning': (True, True, True),
        'off': (False, False, False),
    }

    def __init__(self, input_pin: int, relay_pin: int, led_pins: list):
        ''' Initialize the GPIO pins. '''
        self.input_pin = input_pin
        self.relay_pin = relay_pin
        self.led_pins = led_pins
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(self.input_pin, GPIO.IN) # PIR sensor
        [GPIO.setup(pin, GPIO.OUT) for pin in [*self.led_pins, self.relay_pin]]
        
        self.status = 'starting'
        self.write_relay(False)

    def state_machine(self) -> bool:
        """ The state machine for the pin.
        
        Returns:
            bool: If system should be in weapon detection mode.
        """
        # print('Status: ', self.status, ' Time: ', time.time() - self.start_time)
        if self.status == 'standby' and self.read_pin():
            self.status = 'running' # Set status to running
            return True # Return start time and True
        
        if self.status == 'starting' or self.status == 'learning':
            return False # Return False
        
        elif self.status == 'running' and (time.time() - self.start_time) > 12:
            self.status = 'standby' # Set status to standby
            return False # Return False
        
        elif self.status == 'sent' and time.time() - self.start_time > 15:
            self.status = 'alarm' # Set status to alarm
            return False # Return False
        
        elif (self.status == 'alarm' and time.time() - self.start_time > 60) or self.status == 'password':
            self.status = 'standby' # Set status to standby
            return False
        else:
            return True # Return True
    
    @property
    def status(self) -> str:
        """ Get the status of the pin.

        Returns:
            str: The status of the pin.
        """
        return self._status    

    @status.setter
    def status(self, status: str):
        """ Set the status of the pin.

        Args:
            status (str): The status to set.
        """
        self._status = status
        self.start_time = time.time()
        self.write_rgb(*self.STATUS_COLORS[self.status])
        if status == 'alarm':
            self.write_relay(True)
        else:
            self.write_relay(False)
        print('Status set to: ', self.status)

    def get_status(self) -> str:
        """ Get the status of the pin.

        Returns:
            str: The status of the pin.
        """
        return self.status

    def read_pin(self) -> bool:
        """ Read the value of a pin.

        Returns:
            bool: The value of the pin.
        """        
        
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
        GPIO.output(self.relay_pin, value)
            
    def set_sent_status(self):
        """ Set the status to sent and start the timer. """
        self.status = 'sent'
        self.start_time = time.time()
        self.write_rgb(True, True, False)
        self.write_relay(False)