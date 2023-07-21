# GPIO.BCM
# GPIO.IN
# GPIO.setwarnings
# GPIO.setmode
# GPIO.OUT
# GPIO.input
# GPIO.output
# GPIO.setup

class GPIO:
    BCM = 'BCM'
    IN = 'IN'
    OUT = 'OUT'
    pin_status = None
    def setwarnings(self, *args, **kwargs):
        pass
    def setmode(self, *args, **kwargs):
        pass
    def setup(self, *args, **kwargs):
        pass
    def input(self, *args, **kwargs):
        return self.pin_status
    def output(self, *args, **kwargs):
        pass
