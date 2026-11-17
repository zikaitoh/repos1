from controller import Robot

TIME_STEP = 32
MAX_SPEED = 6.28

robot = Robot()

# -----------------------
# Set Variables
# -----------------------
seen_r = 0
seen_g = 0
seen_b = 0
reported = 0
# -----------------------
# Sensors
# -----------------------
ps = []
psNames = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4', 'ps5', 'ps6', 'ps7'
]

for i in range(8):
    ps.append(robot.getDevice(psNames[i]))
    ps[i].enable(TIME_STEP)
# -----------------------
# Motors
# -----------------------
leftMotor = robot.getDevice('left wheel motor')
rightMotor = robot.getDevice('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

# -----------------------
# Camera
# -----------------------
cam = robot.getDevice('camera')
cam.enable(TIME_STEP)

W = cam.getWidth()
H = cam.getHeight()

def move_forward():
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)
    
def stop():
    leftMotor.setVelocity(0)
    rightMotor.setVelocity(0)

def colSeen():
    summ = "I've seen "
    if seen_r == 1:
        summ = summ + "red, " 
    if seen_g == 1:
        summ = summ + "green, "
    if seen_b == 1:
        summ = summ + "blue "
    print (summ)
# -----------------------
# Main loop
# -----------------------
while robot.step(TIME_STEP) != -1:
 # read sensors outputs
    psValues = []
    for i in range(8):
        psValues.append(ps[i].getValue())

    # detect obstacles
    right_obstacle = psValues[0] > 80.0 or psValues[1] > 80.0 or psValues[2] > 80.0
    left_obstacle = psValues[5] > 80.0 or psValues[6] > 80.0 or psValues[7] > 80.0

    # initialize motor speeds at 50% of MAX_SPEED.
    leftSpeed  = 0.5 * MAX_SPEED
    rightSpeed = 0.5 * MAX_SPEED
    # modify speeds according to obstacles
    if left_obstacle:
        # turn right
        leftSpeed  = 0.5 * MAX_SPEED
        rightSpeed = -0.5 * MAX_SPEED
    elif right_obstacle:
        # turn left
        leftSpeed  = -0.5 * MAX_SPEED
        rightSpeed = 0.5 * MAX_SPEED
    # write actuators inputs
    leftMotor.setVelocity(leftSpeed)
    rightMotor.setVelocity(rightSpeed)        

    # colour detection    
    img = cam.getImage()
    x = W // 2
    y = H // 2

    r = cam.imageGetRed(img, W, x, y)
    g = cam.imageGetGreen(img, W, x, y)
    b = cam.imageGetBlue(img, W, x, y)

    # Red dominance rule (works with your lighting)
    is_red = (r > g + 20) and (r > b + 20)
    is_grn = (g > r + 20) and (g > b + 20)
    is_blu = (b > g + 20) and (b > r + 20)

    if is_red:
        if seen_r == 0:
            print("I see RED!", r, g, b)
            colSeen()
        seen_r = 1
        
    elif is_grn:
        if seen_g == 0:
            print("I see GREEN!", r, g, b)
            colSeen()
        seen_g = 1
        
    elif is_blu:
        if seen_b == 0:
            print("I see BLUE!", r, g, b)
            colSeen()
        seen_b = 1
    elif seen_r == 1 and seen_g == 1 and seen_b == 1 and reported == 0:
        print ("I've seen all colours!")
        reported = 1
