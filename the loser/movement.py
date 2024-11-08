import machine
import time
import _thread
from imu.imu_readings import get_z,set_z
encoder_a_count = 0
encoder_b_count = 0

# Define PID constants
P_constant = 10  # Proportional gain
I_constant = 0.0  # Integral gain
D_constant = 0.0  # Derivative gain

# Initialize PID variables
previous_error = 0.0
integral = 0.0

# Define target orientation (0 degrees)
target_orientation = 0.0

# Function to calculate PID control for motor PWM
def pid_control(orientation_error):
    global previous_error, integral

    # Calculate PID components
    proportional = P_constant * orientation_error
    integral += I_constant * orientation_error
    derivative = D_constant * (orientation_error - previous_error)

    # Calculate PID output
    pid_output = proportional + integral + derivative

    # Update previous error for the next iteration
    previous_error = orientation_error

    # Map the PID output to motor PWM values
    motor_pwm = pid_output  # You'll need to customize this mapping based on your robot's characteristics

    return motor_pwm

def encoderInit():
    # Initialize motors
    # Attach encoder interrupts
    encoder_a_pin_A = machine.Pin(35, machine.Pin.IN)
    encoder_a_pin_B = machine.Pin(34, machine.Pin.IN)
    encoder_b_pin_A = machine.Pin(32, machine.Pin.IN)
    encoder_b_pin_B = machine.Pin(33, machine.Pin.IN)

    # Attach encoder interrupts with callback functions
    encoder_a_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=encoder_a_callback)
    encoder_b_pin_A.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=encoder_b_callback)

def encoder_a_callback(pin):
    global encoder_a_count
    encoder_a_count += 1

def encoder_b_callback(pin):
    global encoder_b_count
    encoder_b_count += 1
            
def get_encoder_a_count():
    global encoder_a_count
    return encoder_a_count

def get_encoder_b_count():
    global encoder_b_count
    return encoder_b_count

# Define GPIO pins for Motor A
motor_b_enable = machine.Pin(13, machine.Pin.OUT)  # Enable pin for Motor A
motor_b_1 = machine.Pin(12, machine.Pin.OUT)       # Control pin 1 for Motor A
motor_b_2 = machine.Pin(14, machine.Pin.OUT)       # Control pin 2 for Motor A

# Define GPIO pins for Motor B
motor_a_enable = machine.Pin(27, machine.Pin.OUT)  # Enable pin for Motor B
motor_a_1 = machine.Pin(26, machine.Pin.OUT)       # Control pin 1 for Motor B
motor_a_2 = machine.Pin(25, machine.Pin.OUT)       # Control pin 2 for Motor B

# Create PWM objects for motor speed control
motor_a_pwm = machine.PWM(motor_a_enable, freq=1000, duty=512)  # Motor A PWM
motor_b_pwm = machine.PWM(motor_b_enable, freq=1000, duty=512)  # Motor B PWM

# Function to set motor A direction and speed
def set_motor_right(direction, speed):
    motor_a_1.value(direction)
    motor_a_2.value(not direction)
    motor_a_pwm.duty(int(speed))

# Function to set motor B direction and speed
def set_motor_left(direction, speed):
    motor_b_1.value(direction)
    motor_b_2.value(not direction)
    motor_b_pwm.duty(int(speed))

# Function to control the motors using encoder counts
def control_motors(target_counts, speed):
    global encoder_a_count, encoder_b_count

    # Reset encoder counts
    encoder_a_count = 0
    encoder_b_count = 0

    # Set motor directions
    set_motor_right(1, 800)
    set_motor_left(1, 725)
    time.sleep(0.2)
    set_z(0)
    while True:
        #print(get_z())
        # Read orientation from IMU (Z-axis)
        current_orientation = get_z()
        # Calculate orientation error (target_orientation - current_orientation)
        orientation_error = 0 - current_orientation

        # Use PID control to calculate motor PWM based on orientation error
        motor_pwm = pid_control(orientation_error)
                # Map motor_pwm to motor speed values
        left_motor_speed = (725 - motor_pwm) 
        right_motor_speed = (800 + motor_pwm) 
        
        if left_motor_speed > 1023:
            left_motor_speed = 1023
        elif left_motor_speed < 300:
            left_motor_speed = 300
            
        if right_motor_speed > 1023:
            right_motor_speed = 1023
        elif right_motor_speed < 300:
            right_motor_speed = 300
            
        set_motor_right(1, right_motor_speed)
        set_motor_left(1, left_motor_speed)
            
        #print("Right", right_motor_speed)
        #print("Left", left_motor_speed)
        time.sleep(0.01)

        if abs(encoder_a_count) >= target_counts or abs(encoder_b_count) >= target_counts:
            break

   
# Function to make the robot move forward
def move_forward():
#     control_motors(1000, 1023)  # Adjust target_counts and speed as needed
    set_motor_right(1, 800)  # Motor A forward at half speed
    set_motor_left(1, 800)  # Motor B forward at full speed 

# Function to make the robot turn right
def move_right():
    set_motor_right(0, 350)  # Motor A forward at half speed
    set_motor_left(1, 350)  # Motor B forward at full speed

# Function to make the robot turn left
def move_left():
    set_motor_right(1, 350)  # Motor A forward at full speed
    set_motor_left(0, 350)  # Motor B forward at half speed

# Function to stop the robot
def move_stop():
    set_motor_right(0, 0)
    set_motor_left(0, 0)

def move_reverse():
    set_motor_right(0, 1023)  # Motor A forward at half speed
    set_motor_left(0, 1023)  # Motor B forward at full speed


