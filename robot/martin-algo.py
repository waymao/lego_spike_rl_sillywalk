# LEGO type:standard slot:5

from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from random import random, choice, randint
from time import sleep, localtime
from hub import port, BT_VCP
from math import *

import ujson


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


# storing history data
history_memory = list(range(0, EPISODE_LEN))
# storing bluetooth data
vcp = BT_VCP(0)

# TODO: add quantized tail angle to the state
S = list(range(-2, 3))
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
    
    
def get_state(theta):
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
    
def get_reward(theta):
    return -exp(abs(theta/180.0))+1

def update_reward_history(timestep, state, action, new_state, reward):
    history_memory[timestep] = (state, action, reward)

def send_reward_history():
    encoded_hist = ujson.dumps({"history": history_memory})
    vcp.write(encoded_hist)
    vcp.write('/n/n/n')

def q_error(s, a, r, new_s):
    return r + GAMMA*max(Q[S.index(new_s)]) - Q[s][a]

def emote(r):
    if r < -1:
        hub.light_matrix.show_image('ANGRY')
    elif r < -0.5:
        hub.light_matrix.show_image('SAD')
    else:
        hub.light_matrix.show_image('HAPPY')

def Q_learning():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0
        while step < EPISODE_LEN:
            theta = hub.motion_sensor.get_yaw_angle()
            s = get_state(theta)
            a = epi_greedy(s)
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            new_theta = hub.motion_sensor.get_yaw_angle()
            new_s = get_state(new_theta)
            r = get_reward(new_theta)
            Q[s][a] += ALPHA*q_error(s, a, r, new_s)
            step += 1

def et_q_error(s, a, new_s, new_a, r):
    return r + GAMMA*Q[new_s][new_a] - Q[s][a]

def et_Q_learning():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0
        s = get_state(hub.motion_sensor.get_yaw_angle())
        a = epi_greedy(s)
        while step < EPISODE_LEN:
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            theta = hub.motion_sensor.get_yaw_angle()
            new_s = get_state(theta)
            new_a = epi_greedy(new_s)
            r = get_reward(theta)
            emote(r)
            update_reward_history(timestep=step, state=s, action=new_a, new_state=new_s, reward=r)
            delta = et_q_error(s, a, new_s, new_a, r)
            E[s][a] += 1
            for each_s in S:
                for each_a in A_i:
                    Q[each_s][each_a] += ALPHA * delta * E[each_s][each_a]
                    E[each_s][each_a] = GAMMA * LAMBDA * E[each_s][each_a]
            s = new_s
            a = new_a
            step += 1
        send_reward_history()

et_Q_learning()


def sarsa_lambda():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0

        # initialize s, a
        s = get_state()
        a = epi_greedy(s)
        
        while step < EPISODE_LEN:
            do_action(A[a])
            new_s = get_state()
            new_a = epi_greedy(new_s)
            r = get_reward()
            delta = et_q_error(s, a, new_s, new_a, r)
            E[s][a] += 1
            for each_s in S:
                for each_a in A_i:
                    Q[each_s][each_a] += ALPHA * delta * E[each_s][each_a]
                    E[each_s][each_a] = GAMMA * LAMBDA * E[each_s][each_a]
            s = new_s
            a = new_a
            step += 1


def Q_learning():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0
        while step < EPISODE_LEN:
            s = get_state()
            a = epi_greedy(s)
            do_action(A[a])
            new_s = get_state()
            r = get_reward()
            Q[s][a] += ALPHA*q_error(s, a, r, new_s)
            step += 1