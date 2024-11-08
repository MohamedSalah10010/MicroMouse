from time import sleep
from encoder.encoder_readings import RobotEncoder
from imu.imu_readings import imu_data
from ultrasonic.ultrasonic_readings import  RobotUltrasonic
from movement import forward, reverse, right, left

while True:
    forward()
    time.sleep(0.1)
