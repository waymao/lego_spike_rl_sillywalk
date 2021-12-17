# LEGO type:standard slot:5

from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from random import random, choice, randint
from time import sleep, localtime
from hub import port
from math import *

hub = PrimeHub()
left_motor_prime = Motor('A')
right_motor_prime = Motor('B')
tail_motor_prime = Motor('D')

left_motor = port.A.motor
right_motor = port.B.motor
tail_motor = port.D.motor

hub.motion_sensor.reset_yaw_angle()
hub.light_matrix.show_image('HAPPY')

EPSILON = 0.1
GAMMA = 0.9
LAMBDA = 0.3
ALPHA = 0.1

INTERVAL = 0.5
WIDE_ANGLE = 45
NARROW_ANGLE = 15
EPISODE_LEN = 90

LR_SPEED = 45
TAIL_SPEED = 25

LR_DOM = list(range(0, 2))
T_DOM = [-1, 1]
YALL_DOM = list(range(-2, 3))
TAIL_DOM = list(range(-1, 2))

############## history ################
def reset_reward_history():
    global sum_yaw, sum_reward, history_memory
    sum_yaw = 0
    sum_reward = 0
    history_memory = [None] * EPISODE_LEN
reset_reward_history()

def update_reward_history(timestep, state, action, new_state, reward, yaw):
    global sum_yaw, sum_reward, history_memory
    history_memory[timestep] = (state, action, new_state, reward, yaw)
    sum_yaw += yaw * yaw
    sum_reward += reward

def send_reward_history(episode=0):
    print({
        "history": history_memory, 
        "episode": episode, 
        "yaw_avg": sqrt(sum_yaw) / EPISODE_LEN,
        "rew_avg": sum_reward / EPISODE_LEN
    })
############## END history ################ 

# TODO: add quantized tail angle to the state
# S = YALL_DOM
S = [(i, j) for i in YALL_DOM for j in TAIL_DOM]
A = [(i, j, k) for i in LR_DOM for j in LR_DOM for k in T_DOM]
for i in reversed(range(len(A))):
    if A[i][0]==A[i][1]:
        A.pop(i)
A_i = list(range(len(A)))
Q = [[0]*len(A) for _ in range(len(S))]
E = [[0]*len(A) for _ in range(len(S))]

def epi_greedy(s):
    if random()<EPSILON:
        return randint(0, len(A)-1)
    else:
        max_i = 0
        max_v = Q[s][0]
        for i in range(len(Q[s])):
            if Q[s][i] > max_v:
                max_v = Q[s][i]
                max_i = i
        return max_i

def do_action(a):
    l, r, t = a

    left_motor.run_at_speed(-LR_SPEED*l)
    right_motor.run_at_speed(LR_SPEED*r)
    tail_motor.run_at_speed(TAIL_SPEED*t)

def motors_reset(back): 
    left_motor.run_at_speed(0)
    right_motor.run_at_speed(0)
    if back:
        tail_motor.run_at_speed(0)
    left_motor_prime.run_to_position(300)
    right_motor_prime.run_to_position(70)
    if back:
        tail_motor_prime.run_to_position(0, direction='shortest path')
    
    
def get_state(yall, tail):
    t = 0
    if (tail > WIDE_ANGLE):
        if (tail > 270 - WIDE_ANGLE):
            t = 1
        else:
            t = -1
    
    y = 0
    if yall < -WIDE_ANGLE:
        y = -2
    elif yall > WIDE_ANGLE:
        y = 2
    elif yall < -NARROW_ANGLE:
        y = -1
    elif yall > NARROW_ANGLE:
        y = 1

    s = (y, t)
    return S.index(s)

    
def get_reward(yall):
    return -exp(abs(yall/180.0))+1

def q_error(s, a, r, new_s):
    return r + GAMMA*max(Q[new_s]) - Q[s][a]

def emote(r):
    if r < -1:
        hub.light_matrix.show_image('ANGRY')
    elif r < -0.5:
        hub.light_matrix.show_image('SAD')
    else:
        hub.light_matrix.show_image('HAPPY')

def Q_learning():
    episode = 0
    while True:
        episode += 1
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0
        reset_reward_history()
        while step < EPISODE_LEN:
            yall = hub.motion_sensor.get_yaw_angle()
            tail = tail_motor_prime.get_position()
            s = get_state(yall, tail)
            a = epi_greedy(s)
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            new_yall = hub.motion_sensor.get_yaw_angle()
            new_tail = tail_motor_prime.get_position()
            new_s = get_state(new_yall, new_tail)
            r = get_reward(new_yall)
            update_reward_history(step, s, a, new_s, r, new_yall)
            emote(r)
            Q[s][a] += ALPHA*q_error(s, a, r, new_s)
            step += 1
        send_reward_history(episode)

Q_learning()

# def et_q_error(s, a, new_s, new_a, r):
#     return r + GAMMA*Q[new_s][new_a] - Q[s][a]

# def et_Q_learning():
#     while True:
#         motors_reset(True)
#         hub.left_button.wait_until_pressed()
#         hub.motion_sensor.reset_yaw_angle()
#         step = 0
#         s = get_state(hub.motion_sensor.get_yaw_angle())
#         a = epi_greedy(s)
#         while step < EPISODE_LEN:
#             do_action(A[a])
#             wait_for_seconds(INTERVAL)
#             theta = hub.motion_sensor.get_yaw_angle()
#             new_s = get_state(theta)
#             new_a = epi_greedy(new_s)
#             r = get_reward(theta)
#             emote(r)
#             delta = et_q_error(s, a