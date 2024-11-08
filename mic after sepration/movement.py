import machine
import time

# Define GPIO pins for Motor A
motor_a_enable = machine.Pin(13, machine.Pin.OUT)  # Enable pin for Motor A
motor_a_1 = machine.Pin(12, machine.Pin.OUT)       # Control pin 1 for Motor A
motor_a_2 = machine.Pin(14, machine.Pin.OUT)       # Control pin 2 for Motor A

# Define GPIO pins for Motor B
motor_b_enable = machine.Pin(27, machine.Pin.OUT)  # Enable pin for Motor B
motor_b_1 = machine.Pin(26, machine.Pin.OUT)       # Control pin 1 for Motor B
motor_b_2 = machine.Pin(25, machine.Pin.OUT)       # Control pin 2 for Motor B

# Create PWM objects for motor speed control
motor_a_pwm = machine.PWM(motor_a_enable, freq=1000, duty=512)  # Motor A PWM
motor_b_pwm = machine.PWM(motor_b_enable, freq=1000, duty=512)  # Motor B PWM

# Define GPIO pins for Motor encoders
encoder_a_pin_A = machine.Pin(35, machine.Pin.IN)
encoder_a_pin_B = machine.Pin(34, machine.Pin.IN)
encoder_b_pin_A = machine.Pin(32, machine.Pin.IN)
encoder_b_pin_B = machine.Pin(33, machine.Pin.IN)

# Function to set motor A direction and speed
def _set_motor_right(direction, speed):
    motor_a_1.value(direction)
    motor_a_2.value(not direction)
    motor_a_pwm.duty(speed)

# Function to set motor B direction and speed
def _set_motor_left(direction, speed):
    motor_b_1.value(direction)
    motor_b_2.value(not direction)
    motor_b_pwm.duty(speed)

# Function to control the motors using encoder counts
def control_motors(target_counts, speed):
    encoder_a_count, encoder_b_count

    # Reset encoder counts
    encoder_a_count = 0
    encoder_b_count = 0

    # Set motor directions
    set_motor_right(1, speed)
    set_motor_left(1, speed)

    while True:
        if abs(encoder_a_count) >= target_counts or abs(encoder_b_count) >= target_counts:
            break

   
# Function to make the robot move forward
def forward():
#     control_motors(1000, 1023)  # Adjust target_counts and speed as needed
    set_motor_right(1, 1023)  # Motor A forward at half speed
    set_motor_left(1, 1023)  # Motor B forward at full speed

# Function to make the robot turn right
def right():
    set_motor_right(0, 500)  # Motor A forward at half speed
    set_motor_left(1, 1023)  # Motor B forward at full speed

# Function to make the robot turn left
def left():
    set_motor_right(1, 1023)  # Motor A forward at full speed
    set_motor_left(0, 500)  # Motor B forward at half speed

# Function to stop the robot
def stop():
    set_motor_right(0, 0)
    set_motor_left(0, 0)

def reverse():
    set_motor_right(0, 1023)  # Motor A forward at half speed
    set_motor_left(0, 1023)  # Motor B forward at full speed


