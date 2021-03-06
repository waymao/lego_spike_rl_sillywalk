from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from random import random, choice, randint
from time import sleep
from math import *
import utime
import hub as ct_hub

hub = PrimeHub()
left_motor = Motor('A')
right_motor = Motor('B')
tail_motor = Motor('D')
#button = ForceSensor('E')

hub.light_matrix.show_image('ASLEEP')

EPSILON = 0.1
GAMMA = 0.9
LAMBDA = 0.9
ALPHA = 0.1

HUMAN_COEFF = 0.2

ARM_STEP_SIZE = 360
TAIL_STEP_SIZE = 60
WIDE_ANGLE = 45
NARROW_ANGLE = 15
EPISODE_LEN = 25

SPEED = 50
TAIL_MIN = 70
TAIL_MAX = 290

LR_DOM = list(range(0, 2))
T_DOM = list(range(-1, 2))

S = list(range(-2, 3))
A = [(i, j, k) for i in LR_DOM for j in LR_DOM for k in T_DOM]
for i in reversed(range(len(A))):
    if A[i][0]==0 and A[i][1]==0:
        A.pop(i)

Q = [[0]*len(A) for _ in range(len(S))]
# e = {(s, a):0 for s in S for a in A}

def epi_greedy(s):
    if random()<EPSILON:
        return randint(0, len(A))
    else:
        return Q[s].index(max(Q[s]))

# begin receive signal
vcp = ct_hub.USB_VCP(0)
def receive_human_feedback():
    if not vcp.isconnected():
        return 0
    
    vcp.write(("\nready to accept human feedback\n").encode())
    ct_hub.display.show(ct_hub.Image.PACMAN)
    reward = 0
    for i in range(50): # 5cgcc seconds wait
        if vcp.any():
            while vcp.any():
                line = vcp.readline()
                if line is not None:
                    line_decoded = line.decode("ascii")
                    reward = word_to_reward(line_decoded)
                    vcp.write(("\nyou sent \"" + 
                        line_decoded + 
                        "\" which have reward " + 
                        str(reward) +
                        "\n").encode())
                else:
                    vcp.write(("\nyou sent None\n").encode())
        utime.sleep(0.1)
    ct_hub.display.show(ct_hub.Image.ARROW_E)
    vcp.write(("\nresuming operation...\n").encode())
    return reward

def word_to_reward(word):
    if word == "bad":
        return -1
    elif word == "good":
        return 1
    else:
        return 0

def do_action(a):
    l, r, t = a
    left_motor.run_for_degrees(l*ARM_STEP_SIZE, speed=-SPEED)
    right_motor.run_for_degrees(r*ARM_STEP_SIZE, speed=SPEED)
    tail_pos = (tail_motor.get_position() + t*TAIL_STEP_SIZE) % 360
    if tail_pos>TAIL_MIN and tail_pos<TAIL_MIN+TAIL_STEP_SIZE:
        tail_pos = TAIL_MIN
    if tail_pos<TAIL_MAX and tail_pos>TAIL_MAX-TAIL_STEP_SIZE:
        tail_pos = TAIL_MAX
    tail_motor.run_to_position(tail_pos, direction='shortest path')
    
def get_state():
    theta = hub.motion_sensor.get_yaw_angle()
    if theta < -WIDE_ANGLE:
        return -2
    elif theta > WIDE_ANGLE:
        return 2
    elif theta < -NARROW_ANGLE:
        return -1
    elif theta > NARROW_ANGLE:
        return 1
    else:
        return 0
    
def get_reward(s):
    return abs(s)*-1

def q_error(s, a, r, new_s):
    return r + GAMMA*max(Q[S.index(new_s)]) - Q[s][a]

def Q_learning():
    while True:
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0
        while step < EPISODE_LEN:
            s = get_state()
            a = epi_greedy(s)
            do_action(A[a])
            sleep(0.5)

            human_feedback = receive_human_feedback()
            new_s = get_state()
            Q[s][a] += ALPHA * q_error(s, a, get_reward(new_s), new_s)
            # human feedback
            if human_feedback != 0:
                Q[s][a] += ALPHA * q_error(s, a, human_feedback * HUMAN_COEFF, new_s)
            step += 1

ct_hub.display.show(ct_hub.Image.ARROW_E)
Q_learning()
