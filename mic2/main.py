from hcsr04 import HCSR04
import machine
import time
import _thread


encoder_a_count = 0
encoder_b_count = 0

class Robot:
    def init(self):
        # Initialize motors
        self.motor_a_enable = machine.Pin(13, machine.Pin.OUT)
        self.motor_a_1 = machine.Pin(12, machine.Pin.OUT)
        self.motor_a_2 = machine.Pin(14, machine.Pin.OUT)
        self.motor_b_enable = machine.Pin(27, machine.Pin.OUT)
        self.motor_b_1 = machine.Pin(26, machine.Pin.OUT)
        self.motor_b_2 = machine.Pin(25, machine.Pin.OUT)
        self.motor_a_pwm = machine.PWM(self.motor_a_enable, freq=1000, duty=512)
        self.motor_b_pwm = machine.PWM(self.motor_b_enable, freq=1000, duty=512)
        
        # Initialize ultrasonic sensors
        self.sensor_middle = HCSR04(trigger_pin=17, echo_pin=5, echo_timeout_us=10000)
        self.sensor_left = HCSR04(trigger_pin=15, echo_pin=2, echo_timeout_us=10000)
        self.sensor_right = HCSR04(trigger_pin=4, echo_pin=16, echo_timeout_us=10000)

        # Attach encoder interrupts
        self.encoder_a_pin_A = machine.Pin(35, machine.Pin.IN)
        self.encoder_a_pin_B = machine.Pin(34, machine.Pin.IN)
        self.encoder_b_pin_A = machine.Pin(32, machine.Pin.IN)
        self.encoder_b_pin_B = machine.Pin(33, machine.Pin.IN)


        self.encoder_a_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.encoder_a_callback)
        self.encoder_b_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=self.encoder_b_callback)
        
        self.distance_middle = 0
        self.distance_left = 0
        self.distance_right = 0

        # Create a lock for accessing shared variables
        self.lock = _thread.allocate_lock()

        # Create a thread for reading ultrasonic sensors
        _thread.start_new_thread(self.read_sensors, ())
        
    def read_sensors(self):
        while True:
            # Read the ultrasonic sensors
            distance_middle = self.sensor_middle.distance_cm()
            distance_left = self.sensor_left.distance_cm()
            distance_right = self.sensor_right.distance_cm()
            print("Middle: ",distance_middle)
            print("Left: ",distance_left)
            print("Right: ",distance_right)
            # Acquire the lock to update shared variables
            with self.lock:
                self.distance_middle = distance_middle
                self.distance_left = distance_left
                self.distance_right = distance_right

            # Sleep for 0.5 seconds before the next reading
            time.sleep(0.5)
            
    def encoder_a_callback(self, pin):
        global encoder_a_count
        encoder_a_count += 1


    def encoder_b_callback(self, pin):
        global encoder_b_count
        encoder_b_count += 1

    def set_motor_speed(self, motor, speed):
        motor[0].value(speed > 0)
        motor[1].value(speed < 0)
        motor[2].duty(abs(speed))

    def move(self, left_speed, right_speed):
        self.set_motor_speed((self.motor_a_1, self.motor_a_2, self.motor_a_pwm), left_speed)
        self.set_motor_speed((self.motor_b_1, self.motor_b_2, self.motor_b_pwm), right_speed)
        
    def control_motors(self, target_counts, speed, direction):
        global encoder_a_count, encoder_b_count
        # Reset encoder counts
        encoder_a_count = 0
        encoder_b_count = 0

        # Set motor directions based on the 'direction' parameter
        if direction == 'forward':
            self.move(speed, speed)
        elif direction == 'backward':
            self.move(-speed, -speed)
        elif direction == 'left':
            self.move(speed, -speed)
        elif direction == 'right':
            self.move(-speed, speed)

        while True:
            if abs(encoder_a_count) >= target_counts or abs(encoder_b_count) >= target_counts:
                break
        # Stop motors
        self.stop()

    def stop(self):
        self.move(0, 0)