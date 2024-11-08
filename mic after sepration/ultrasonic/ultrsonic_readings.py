from hcsr04 import HCSR04
import machine
import time
import _thread



class Robot:
    def __init__(self):
        # Initialize ultrasonic sensors
        self.sensor_middle = HCSR04(trigger_pin=17, echo_pin=5, echo_timeout_us=10000)
        self.sensor_left = HCSR04(trigger_pin=15, echo_pin=2, echo_timeout_us=10000)
        self.sensor_right = HCSR04(trigger_pin=4, echo_pin=16, echo_timeout_us=10000)

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
            # Acquire the lock to update shared variables
            with self.lock:
                self.distance_middle = distance_middle
                self.distance_left = distance_left
                self.distance_right = distance_right

            # Sleep for 0.5 seconds before the next reading
            time.sleep(0.5)
            
    
    
    def distance(self, sensor, num_samples=2):
        total_distance = 0
        for _ in range(num_samples):
            distance = sensor.distance_cm()
            if distance >= 0:
                total_distance += distance
            else:
                total_distance += 20  # Default value if measurement fails
        return total_distance / num_samples  # Calculate the average distance
    
    def adc(reading):
        threshold = 18
        return 1 if reading > threshold else 0

    def ultra_data():
        middle = adc(distance(self, sensor_middle, 2))
        left = adc(distance(self, sensor_left, 2))
        right = adc(distance(self, sensor_right, 2))
        return left, middle, right
    