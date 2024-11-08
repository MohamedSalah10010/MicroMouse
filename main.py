from imu import MPU6050
import time
import machine

# Initialize I2C communication (adjust pins as needed)
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(21))

# Initialize the MPU6050 sensor
mpu = MPU6050(i2c)

# Initialize LED pin
led_pin = machine.Pin(2, machine.Pin.OUT)
led_state = False  # Initially turned off

# Initialize variables
angle_x = 0.0  # Initial angle
angle_z=0.0
angle_y =0
while True:
    # Read gyroscope data
    gyro_data = mpu.gyro

    # Access individual components
    gyro_x = gyro_data.x
    gyro_y = gyro_data.y
    gyro_z = gyro_data.z

    # Calculate angular velocity in degrees per second
    angular_velocity_x = gyro_x / 131.0  # Sensitivity: 131 LSB/(degrees/s)

    # Integrate angular velocity to get angle (simple integration)
    angle_x += angular_velocity_x  # Adjust time interval as needed

    # Check if the angle has reached 90 degrees
    if angle_z >= 90.0 and not led_state:
        led_pin.on()  # Turn on the LED
        led_state = True

    # Print the angle
    print("Angle z: {:.2f} degrees".format(angle_x))

    time.sleep(0.01)  # Adjust the sampling rate as needed
