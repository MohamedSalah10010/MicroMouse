# MicroMouse

An autonomous maze-solving robot built for a **Micromouse competition**, where a small robot must find its way through a maze to the goal in the shortest possible time.

The firmware is written in **MicroPython** and runs on an **ESP32**. The robot senses walls with ultrasonic sensors, keeps track of its heading with a gyroscope, measures distance travelled with wheel encoders, and explores the maze with a depth-first search (DFS) that builds a map as it goes.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Hardware](#hardware)
- [Pin Mapping](#pin-mapping)
- [Software Architecture](#software-architecture)
- [Maze Exploration Algorithm](#maze-exploration-algorithm)
- [Motion Control](#motion-control)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Tuning Guide](#tuning-guide)
- [Known Limitations](#known-limitations)
- [Possible Improvements](#possible-improvements)
- [Acknowledgements](#acknowledgements)

---

## How It Works

Each step through the maze follows the same loop:

```text
Read walls (left / front / right)
        │
        ▼
Update maze map and position
        │
        ▼
Choose next direction (DFS with priority rules)
        │
        ▼
Rotate using the gyroscope (90° / 180°)
        │
        ▼
Drive forward one cell using encoders
(gyro-based PID keeps the robot straight)
        │
        ▼
Repeat until the centre of the maze is reached
```

The maze is modeled as a **16 × 16 grid**. The goal is the **2 × 2 block in the centre** of the maze, cells `(7,7)`, `(7,8)`, `(8,7)` and `(8,8)`. The robot starts at `(0,0)`.

---

## Hardware

| Component | Quantity | Purpose |
|---|---|---|
| ESP32 development board | 1 | Main controller (MicroPython, runs at 240 MHz) |
| HC-SR04 ultrasonic sensor | 3 | Wall detection: left, front, right |
| MPU6050 IMU | 1 | Gyroscope for turning and heading correction |
| DC motors with encoders | 2 | Drive and distance measurement |
| H-bridge motor driver | 1 | Direction and PWM speed control for both motors |

---

## Pin Mapping

### Motors

| Signal | Motor A | Motor B |
|---|---|---|
| Enable / PWM (1 kHz) | GPIO 13 | GPIO 27 |
| Input 1 | GPIO 12 | GPIO 26 |
| Input 2 | GPIO 14 | GPIO 25 |

### Encoders

| Signal | GPIO |
|---|---|
| Encoder A, channel A | 35 |
| Encoder A, channel B | 34 |
| Encoder B, channel A | 32 |
| Encoder B, channel B | 33 |

Encoder counts are accumulated in interrupt handlers triggered on both rising and falling edges of channel A.

### Ultrasonic Sensors (HC-SR04)

| Sensor | Trigger | Echo |
|---|---|---|
| Front | GPIO 17 | GPIO 5 |
| Left | GPIO 15 | GPIO 2 |
| Right | GPIO 4 | GPIO 16 |

### IMU (MPU6050, I²C)

| Signal | GPIO |
|---|---|
| SCL | 22 |
| SDA | 21 |

---

## Software Architecture

The final version of the firmware is split into small modules:

| Module | Responsibility |
|---|---|
| `main.py` | Maze mapping, DFS path selection, orientation tracking, and the main control loop |
| `movement.py` | Motor control, encoder-based distance driving, and gyro-assisted PID straight-line correction |
| `imu/imu_readings.py` | Background thread that integrates the gyroscope Z-axis into a yaw angle |
| `imu/imu.py`, `imu/vector3d.py` | MPU6050 driver and 3D vector helper |
| `ultrasonic/ultrsonic_readings.py` | Wall detection: converts distances into binary open/blocked readings |
| `ultrasonic/hcsr04.py` | HC-SR04 driver |

---

## Maze Exploration Algorithm

### Wall detection

Each ultrasonic sensor is sampled (averaged over 2 readings), and a threshold of **16 cm** converts the distance into a binary value:

```text
distance > 16 cm  →  1 (open)
distance ≤ 16 cm  →  0 (wall)
```

A failed measurement is treated as 20 cm. The result is a three-value reading `[front, right, left]` for the current cell.

### Mapping and direction choice

- The robot keeps a **16 × 16 map** where each cell stores the open directions found when it was first visited, and a second grid recording which directions were already taken from each cell.
- Readings are converted from the robot's frame (front / right / left) into the **global frame** (`U`, `R`, `D`, `L`) using the robot's last movement direction.
- The next direction is chosen by a `priority()` function that avoids going back the way it came, avoids directions already tried from the same cell, and otherwise prefers `U`, then `R`, then `L`, then `D`.
- Exploration stops when the robot reaches any of the four centre cells.

### Turning

The robot tracks its orientation (`UP`, `RIGHT`, `DOWN`, `LEFT`). To move in the chosen direction it picks the required rotation:

| Rotation | Behavior |
|---|---|
| Right | Spin in place until the gyro yaw reaches about 87° |
| Left | Spin in place until the gyro yaw reaches about 87° |
| Back | Spin in place until the gyro yaw reaches 180° |

---

## Motion Control

### Driving one cell

`control_motors(target_counts, speed)` drives forward until the encoder count reaches the target (30 counts per cell in the current configuration).

### Straight-line correction

While driving, a **proportional controller** on the gyro yaw angle keeps the robot on a straight line:

```text
error      = 0 − current_yaw
correction = Kp × error                (Kp = 10)

left_pwm   = 725 − correction
right_pwm  = 800 + correction          (clamped to 300 – 1023)
```

The different base PWM values (725 vs. 800) compensate for the two motors not being perfectly matched.

### Yaw estimation

A background thread reads the MPU6050 gyro Z-axis every 20 ms and integrates it over the elapsed time to produce a yaw angle. A small constant offset is subtracted on each step as a simple drift correction. The angle is reset to zero before each turn and each straight segment.

---

## Repository Structure

```text
MicroMouse/
│
├── the loser/                  # Most complete version: full DFS maze solver
│   ├── main.py                 # Mapping, path selection, orientation, main loop
│   ├── movement.py             # Motors, encoders, PID straight driving
│   ├── imu/
│   │   ├── imu.py              # MPU6050 driver
│   │   ├── imu_readings.py     # Yaw integration thread
│   │   └── vector3d.py
│   └── ultrasonic/
│       ├── hcsr04.py           # HC-SR04 driver
│       └── ultrsonic_readings.py   # Wall detection
│
├── mic after sepration/        # Earlier modular split (sensors / movement in separate files)
├── mic2/                       # Earlier single-class obstacle-avoidance prototype
│
├── main.py                     # Standalone gyro test (angle integration, LED at 90°)
├── hcsr04.py                   # Ultrasonic driver
├── imu.py, mpu6050.py          # IMU drivers
├── vector3d.py
├── boot.py
│
└── lib/                        # Third-party MicroPython libraries (see Acknowledgements)
```

### Version history

The repository keeps the evolution of the project:

1. **`mic2/`**: first prototype. A single `Robot` class with simple reactive obstacle avoidance (go forward if the front is clear, otherwise turn toward whichever side is open).
2. **`mic after sepration/`**: sensors, encoders, IMU and movement separated into their own modules.
3. **`the loser/`**: the most complete version, adding the 16 × 16 map, DFS exploration, gyro-based turns and PID straight-line driving.

---

## Getting Started

### Requirements

- ESP32 board flashed with [MicroPython](https://micropython.org/download/ESP32_GENERIC/)
- A tool to upload files, such as [`mpremote`](https://docs.micropython.org/en/latest/reference/mpremote.html), Thonny, or `ampy`

### Upload the firmware

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd MicroMouse
   ```

2. Copy the contents of the `the loser/` folder to the root of the ESP32 filesystem, keeping the `imu/` and `ultrasonic/` subfolders:

   ```bash
   cd "the loser"
   mpremote cp -r imu :
   mpremote cp -r ultrasonic :
   mpremote cp main.py movement.py :
   ```

3. Wire the hardware according to the [pin mapping](#pin-mapping).

4. Place the robot at the start cell, facing the maze, and reset the board. `main.py` runs automatically on boot.

### Testing individual parts

- **Gyro:** run the top-level `main.py` to print the integrated angle from the MPU6050.
- **Ultrasonic sensors:** call `RobotUltrasonic().ultra_data()` from the REPL to see the open/blocked readings.
- **Movement:** uncomment the example calls at the bottom of `the loser/main.py` (for example `control_motors(...)` and `Rotation(...)`) to test driving and turning in isolation.

---

## Tuning Guide

Values you will most likely need to adjust for a different robot or maze:

| Parameter | File | Default | Notes |
|---|---|---|---|
| `encoder_counts` | `main.py` | 30 | Encoder counts per maze cell; depends on wheel size and cell width |
| Wall threshold | `ultrsonic_readings.py` | 16 cm | Distance below which a wall is detected |
| Turn angle | `main.py` (`Rotation`) | 87° | Slightly under 90° to account for the robot still turning while braking |
| `P_constant` | `movement.py` | 10 | Proportional gain for heading correction |
| Base motor PWM | `movement.py` | 725 / 800 | Compensates for motor mismatch |
| Drift offset | `imu_readings.py` | 0.04351 | Gyro drift correction per step; recalibrate for your IMU |

---

## Known Limitations

- **Exploration only.** The current code explores the maze and stops at the centre. It does not yet run a second optimized pass along the shortest path, so it does not use the "fastest run" part of a Micromouse competition.
- **DFS is not shortest-path.** The route found by DFS is not guaranteed to be the shortest one.
- **Ultrasonic sensors** are slower and less precise than the infrared sensors typically used in Micromouse robots, and can give unreliable readings near corners.
- **Stop-and-go movement.** The robot stops at every cell to read sensors and turn, which limits speed.
- **Gyro drift.** Yaw is obtained by integrating gyro readings, so errors accumulate over time. Resetting the angle before each segment limits this.
- **Hard-coded values.** Thresholds, PWM values and turn angles are tuned for one specific robot.

---

## Possible Improvements

- Add a **flood-fill** algorithm to compute the shortest path to the goal
- Run a second **speed run** along the optimized path after exploration
- Replace ultrasonic sensors with **IR distance sensors** for faster, more accurate wall detection
- Add **PID speed control** using encoder feedback for each wheel
- Use **sensor fusion** (accelerometer and gyroscope) for a more stable heading estimate
- Combine consecutive straight cells into one smooth drive instead of stopping in each cell
- Save the explored maze to flash memory so it survives a reset
- Clean up duplicated files and unify the module layout



