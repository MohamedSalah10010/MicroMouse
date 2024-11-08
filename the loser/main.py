import machine
from time import sleep
from imu.imu_readings import get_z, imu_init,set_z
from ultrasonic.ultrsonic_readings import RobotUltrasonic
from movement import*


encoder_counts = 30
UP = 0
RIGHT = 1
DOWN = 2
LEFT = 3
orientation_status = 0

def global_orientation(from_C, now_C, ultra_reads):
    dic = {0: "U", 1: "R", 2: "L", 3: "D"}
    open_path = []
    direction = "U"

    # determine direction of robot
    x = now_C[0] - from_C[0]
    y = now_C[1] - from_C[1]
    if x == 1 and y == 0: direction = "R"
    elif x == -1 and y == 0: direction = "L"
    elif x == 0 and y == 1: direction = "U"
    elif x == 0 and y == -1: direction = "D"
    # return robot direction and available paths
    if direction == 'U':
        # available paths to go
        for ind in range(3):
            if ultra_reads[ind]: open_path.append(dic[ind])
        return direction, ''.join(open_path) + 'D'
    elif direction == 'R':
        #URL
        # U => R
        # R => D
        # L => U
        dic = {0: "R", 1: "D", 2: "U", 3: "L"}
        for ind in range(3):
            if ultra_reads[ind]: open_path.append(dic[ind])
        return direction, ''.join(open_path) + 'L'
    elif direction == 'L':
        #URL
        # U => L
        # R => U
        # L => D
        dic = {0: "L", 1: "U", 2: "D", 3: "R"}
        for ind in range(3):
            if ultra_reads[ind]: open_path.append(dic[ind])
        return direction, ''.join(open_path) + 'R'
    elif direction == 'D':
        #URL
        # U => D
        # R => L
        # L => R
        dic = {0: "D", 1: "L", 2: "R", 3: "U"}
        for ind in range(3):
            if ultra_reads[ind]: open_path.append(dic[ind])
        return direction, ''.join(open_path) + 'U'


def priority(inp, last, visited):
    if len(inp) == 1:
        return inp
    if 'U' in visited or last == 'D':
        inp = inp.replace('U', '')
    elif 'L' in visited or last == 'R':
        inp = inp.replace('L', '')
    elif 'R' in visited or last == 'L':
        inp = inp.replace('R', '')
    elif 'D' in visited or last == 'U':
        inp = inp.replace('D', '')

    # print(inp, visited, last)
    if len(inp) > 1 and len(visited) > 0:
        if 'U' in inp and 'U' != last:
            return 'U'
        elif 'R' in inp and 'R' != last:
            return 'R'
        elif 'L' in inp and 'L' != last:
            return 'L'
        elif 'D' in inp and 'D' != last:
            return 'D'

    if 'U' in inp:
        return 'U'
    elif 'R' in inp:
        return 'R'
    elif 'L' in inp:
        return 'L'
    elif 'D' in inp:
        return 'D'
    else:
        last

x, y = 16, 16

map = [['' for _ in range(x)] for _ in range(y)]

visited = [['' for _ in range(x)] for _ in range(y)]
flag = True
ultrasonics = []
pos = [0, 0]



#ultrasonics = [[1, 0, 0], [1, 0, 0], [1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 1, 0], [0, 0, 0], [0, 0, 1], [1, 0, 1], [1, 0, 0], [0, 0, 1], [1, 0, 0], [0, 1, 1], [1,0, 0], [0, 0, 0]]
old_pos = [0, 0]

path = ''
paths = []
def dfs(ultrasonics):
    global map, path, old_pos, pos,flag
    print(path, pos)
    if pos in [[7, 7], [7, 8], [8, 7], [8, 8]]:  #
        flag = False
        print("maze solved")
        move_stop()
        return path
    next = global_orientation(old_pos, pos, ultrasonics[-1])
    old_pos = pos[::]
    if len(map[pos[0]][pos[1]]) > 0:
        chr = next[0]
        if chr == 'D':
            chr = 'U'
        elif chr == 'R':
            chr = 'L'
        elif chr == 'L':
            chr = 'R'
        elif chr == 'U':
            chr = 'D'
        map[pos[0]][pos[1]] = map[pos[0]][pos[1]].replace(chr, '')
    else:
        map[pos[0]][pos[1]] = next[1]
    n = priority(next[1], next[0], visited[pos[0]][pos[1]])
    path += n
    visited[old_pos[0]][old_pos[1]] += n
    if n == "U":
        pos[1] += 1
    elif n == "R":
        pos[0] += 1
    elif n == "L":
        pos[0] -= 1
    elif n == "D":
        pos[1] -= 1
    # print(path)
# print(*map)

for _ in range(len(path)):
    x = path
    for i in range(len(path)-1):
        x = x.replace("RL", "")
        x = x.replace("DU", "")
        x = x.replace("UD", "")
        x = x.replace("LR", "")
    path = x



machine.freq(240000000)
ultrasonic = RobotUltrasonic()
imu_init()
c = 5
encoderInit()
def Rotation(orientation):
    # Set motor directions based on the 'direction' parameter
    print(1)
    if orientation == 'right':
        move_right()
        set_z(0)
        while(abs(get_z()) < 87):
            sleep(0.01)
            pass
        
    elif orientation == 'left':
        move_left()
        set_z(0)
        while(abs(get_z()) < 87):
            sleep(0.01)
            pass
    elif orientation == 'back':
        move_right()
        set_z(0)
        while(abs(get_z()) < 180):
            sleep(0.01)
            pass
def update_orientation(dir):
    global orientation_status, LEFT, UP, DOWN, RIGHT
    if dir == 'right':
        if orientation_status == LEFT:
            orientation_status = UP
        else:
            orientation_status += 1
    elif dir == 'left':
        if orientation_status == UP:
            orientation_status = LEFT
        else:
            orientation_status -= 1
    elif dir == 'back':
        if orientation_status == RIGHT:
            orientation_status = LEFT
        elif orientation_status == UP:
            orientation_status = DOWN
        else:
            orientation_status -= 2
 

while flag:
    print("ready")
    sleep(1)
    temp_list = ultrasonic.ultra_data()
    #print(temp_list)
    surr = list(temp_list)
    #print(surr)
    for i in range(len(surr)):
        surr[i] = int(surr[i])
    ultrasonics.append(surr)
    dfs(ultrasonics)
    if path[-1] == 'U':
        if orientation_status == UP:
            control_motors(encoder_counts, 1023)
        elif orientation_status == DOWN:
            Rotation('back')
            update_orientation('back')
            control_motors(encoder_counts, 1023)
        elif orientation_status == RIGHT:
            Rotation('left')
            update_orientation('left')
            control_motors(encoder_counts, 1023)
        elif orientation_status == LEFT:
            Rotation('right')
            update_orientation('right')
            control_motors(encoder_counts, 1023)
        
    elif path[-1] == 'R':
        if orientation_status == UP:
            Rotation('right')
            update_orientation('right')
            control_motors(encoder_counts, 1023)
        elif orientation_status == DOWN:
            Rotation('left')
            update_orientation('left')
            control_motors(encoder_counts, 1023)
        elif orientation_status == RIGHT:
            control_motors(encoder_counts, 1023)
        elif orientation_status == LEFT:
            Rotation('back')
            update_orientation('back')
            control_motors(encoder_counts, 1023)
    elif path[-1] == 'L':
        if orientation_status == UP:
            Rotation('left')
            update_orientation('left')
            control_motors(encoder_counts, 1023)
        elif orientation_status == DOWN:
            Rotation('right')
            update_orientation('right')
            control_motors(encoder_counts, 1023)
        elif orientation_status == RIGHT:
            Rotation('back')
            update_orientation('back')
            control_motors(encoder_counts, 1023)
        elif orientation_status == LEFT:
            control_motors(encoder_counts, 1023)
    elif path[-1] == 'D':
        if orientation_status == UP:
            Rotation('back')
            update_orientation('back')
            control_motors(encoder_counts, 1023)
        elif orientation_status == DOWN:
            control_motors(encoder_counts, 1023)
        elif orientation_status == RIGHT:
            Rotation('right')
            update_orientation('right')
            control_motors(encoder_counts, 1023)
        elif orientation_status == LEFT:
            Rotation('left')
            update_orientation('left')
            control_motors(encoder_counts, 1023)
    move_stop()
    print(ultrasonics)

   

#while c:
 #   c-=1
    #print(encoder.get_encoder_b_count()
  #  left,middle,right = ultrasonic.ultra_data()
    #print("left: ", left)
    #print("right: ", right)
    #print("middle: ", middle)
    #control_motors(9, 1023)
    #Rotation('right')
    #control_motors(9, 1023)
    #Rotation('back')
    #control_motors(150, 1023)
    #move_stop()
    #Rotation('left')
    #control_motors(150, 1023)
    #move_stop()
    #Rotation('back')
    #control_motors(500, 1023)
    #set_motor_right(1, 600)
    #set_motor_left(1, 537)
    #control_motors(150, 1023)
   # move_stop()
    #sleep(5)
    
    

