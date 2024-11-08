import machine
import time
import _thread

class Robot:
    def __init__(self):
        # Initialize motors
        # Attach encoder interrupts
        self.encoder_a_pin_A = machine.Pin(35, machine.Pin.IN)
        self.encoder_a_pin_B = machine.Pin(34, machine.Pin.IN)
        self.encoder_b_pin_A = machine.Pin(32, machine.Pin.IN)
        self.encoder_b_pin_B = machine.Pin(33, machine.Pin.IN)

        # Initialize encoder count variables
        self.encoder_a_count = 0
        self.encoder_b_count = 0

        # Create locks for accessing shared variables
        self.lock_a = _thread.allocate_lock()
        self.lock_b = _thread.allocate_lock()

        # Attach encoder interrupts with callback functions
        self.encoder_a_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.encoder_a_callback)
        self.encoder_b_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.encoder_b_callback)

    def encoder_a_callback(self, pin):
        with self.lock_a:
            self.encoder_a_count += 1

    def encoder_b_callback(self, pin):
        with self.lock_b:
            self.encoder_b_count += 1
            
    def get_encoder_a_count(self):
        with self.lock_a:
            return self.encoder_a_count

    def get_encoder_b_count(self):
        with self.lock_b:
            return self.encoder_b_count

# Create an instance of the Robot class
#robot = Robot()

# Example usage
#while True:
 #   print("Encoder A Count:", robot.get_encoder_a_count())
  #  print("Encoder B Count:", robot.get_encoder_b_count())
   # time.sleep(1)

