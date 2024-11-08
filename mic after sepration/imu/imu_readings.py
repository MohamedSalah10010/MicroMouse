import machine
import time
import math
import _thread
from imu import MPU6050
from time import sleep


# Initialize I2C
i2c = machine.I2C(scl=machine.Pin(22), sda=machine.Pin(21), freq=400000)

# Create an instance of the MPU6050 sensor
mpu = MPU6050(i2c)

# Initialize variables
z_rotation = 0.0
last_time = 0.0

# Define a function to continuously update the angle in a separate thread
def update_angle_thread():
    global z_rotation, last_time
    while True:
       #Read accelerometer and gyroscope data
        accel_data = mpu.accel.xyz
        gyro_data = mpu.gyro.xyz

        #Extract gyro rate components
        gyro_z = gyro_data[2]

        #Calculate time delta (dt) since the last reading
        current_time = time.ticks_ms() / 1000
        dt = current_time - last_time
        last_time = current_time

        #Calculate yaw angle using gyroscope data (in degrees)
        z_rotation += gyro_z * dt  # Yaw rate integrated over time

        #Ensure z_rotation stays within [-180, 180] degrees
        z_rotation = (z_rotation + 180) % 360 - 180
        
        print(z_rotation)

        time.sleep(0.5)  # Adjust the sleep duration as needed


 def imu_data():
        _thread.start_new_thread(update_angle_thread, ())
        gyro_data = z_rotation
        return gyro_data
 #Start the update_angle_thread function in a separate thread
