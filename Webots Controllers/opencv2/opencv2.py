
"""my_arap controller + RED detection + OpenCV image saving (e-puck)"""
from controller import Robot
import cv2 as cv
import numpy as np
import os

TIME_STEP = 32
MAX_SPEED = 6.28
DIST_LIMIT = 70.0

# RED detection thresholds
R_MIN = 100
G_MIN = 100
B_MIN = 100
R_MAX = 80
G_MAX = 80
B_MAX = 80

robot = Robot()

# Motors
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')

leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# Proximity sensors
rightSensor1 = robot.getDevice('ps0')
rightSensor2 = robot.getDevice('ps1')
leftSensor1 = robot.getDevice('ps7')
leftSensor2 = robot.getDevice('ps6')

rightSensor1.enable(TIME_STEP)
rightSensor2.enable(TIME_STEP)
leftSensor1.enable(TIME_STEP)
leftSensor2.enable(TIME_STEP)

# Camera
cam = robot.getDevice('camera')
cam.enable(TIME_STEP)

W = cam.getWidth()
H = cam.getHeight()

# Create folder to save images
SAVE_FOLDER = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(SAVE_FOLDER, exist_ok=True)

captured_colors = set()   # colors that already have a saved picture


# ----------------------------------
# Proximity sensor functions
# ----------------------------------

def get_left_sensor():
    value1 = leftSensor1.getValue()
    value2 = leftSensor2.getValue()
    average = (value1 + value2) / 2.0
    return average > DIST_LIMIT


def get_right_sensor():
    value1 = rightSensor1.getValue()
    value2 = rightSensor2.getValue()
    average = (value1 + value2) / 2.0
    return average > DIST_LIMIT


# ----------------------------------
# RED object detection
# ----------------------------------

def detect_color():
    """Return 'red', 'green', 'blue', or None based on the center pixel."""
    img = cam.getImage()

    if img is None:
        return None

    x = W // 2
    y = H // 2

    r = cam.imageGetRed(img, W, x, y)
    g = cam.imageGetGreen(img, W, x, y)
    b = cam.imageGetBlue(img, W, x, y)

    if r > R_MIN and g < G_MAX and b < B_MAX:
        return "red"
    if r < R_MAX and g > G_MIN and b < B_MAX:
        return "green"
    if r < R_MAX and g < G_MAX and b > B_MIN:
        return "blue"
    return None

# ----------------------------------
# Capture and save camera image
# ----------------------------------

def save_camera_image(color):

    img = cam.getImage()

    if img is None:
        print("Camera image unavailable")
        return False

    image_array = np.frombuffer(img, dtype=np.uint8).reshape((H, W, 4))
    image_bgr = cv.cvtColor(image_array, cv.COLOR_BGRA2BGR)

    filepath = os.path.join(SAVE_FOLDER, f"{color}_object.jpg")

    if cv.imwrite(filepath, image_bgr):
        print("Image saved:", filepath)
        return True

    print("Failed to save image")
    return False
# ----------------------------------
# Robot movement functions
# ----------------------------------

def stop():
    leftMotor.setVelocity(0.0)
    rightMotor.setVelocity(0.0)


def move_forward():
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)


def move_backward():
    leftMotor.setVelocity(-0.5 * MAX_SPEED)
    rightMotor.setVelocity(-0.5 * MAX_SPEED)


def turn_left():
    leftMotor.setVelocity(0.1 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)


def turn_right():
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.1 * MAX_SPEED)


# ----------------------------------
# Main controller
# ----------------------------------

def main():

    TIME_DELAY = 0.5
    time_start = robot.getTime()

    move_forward()

    while robot.step(TIME_STEP) != -1:

        # Color detection: capture once per color, never stop
        color = detect_color()

        if color is not None and color not in captured_colors:
            print(f"{color.upper()} detected! Capturing image.")
            if save_camera_image(color):
                captured_colors.add(color)

                if len(captured_colors) == 3:
                    print("All three colors captured.")

        # Obstacle avoidance (runs every cycle now)
        time_elapsed = robot.getTime()
        time_diff = time_elapsed - time_start

        if time_diff >= TIME_DELAY:

            blocked_left = get_left_sensor()
            blocked_right = get_right_sensor()

            if blocked_left and blocked_right:
                move_backward()
            elif blocked_left:
                turn_right()
            elif blocked_right:
                turn_left()
            else:
                move_forward()

            time_start = time_elapsed


if __name__ == '__main__':
    main()
