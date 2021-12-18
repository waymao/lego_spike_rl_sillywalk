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
distance = DistanceSensor('C')

left_motor = port.A.motor
right_motor = port.B.motor
tail_motor = port.D.motor

hub.motion_sensor.reset_yaw_angle()
hub.light_matrix.show_image('HAPPY')

EPSILON = 0.1
GAMMA = 0.9
LAMBDA = 0.1
ALPHA = 0.1

INTERVAL = 0.5
WIDE_ANGLE = 45
NARROW_ANGLE = 15
EPISODE_LEN = 50

LR_SPEED = 45
TAIL_SPEED = 25

LR_DOM = list(range(0, 2))
T_DOM = [-1, 1]
YAW_DOM = list(range(-2, 3))

############## history ################


def reset_reward_history():
    global sum_yaw, sum_reward, history_memory
    sum_yaw = 0
    sum_reward = 0
    history_memory = [None] * EPISODE_LEN


reset_reward_history()


def update_reward_history(timestep, state, action, new_state, reward, yaw):
    global sum_yaw, sum_reward, history_memory
    history_memory[timestep] = (reward, yaw)
    sum_yaw += yaw * yaw
    sum_reward += reward


def send_reward_history(episode=0):
    print({
        "history": history_memory,
        "episode": episode,
        # "yaw_mse": sum_yaw / EPISODE_LEN,
        # "rew_sum": sum_reward
    })
############## END history ################


S = [(i, j) for i in YAW_DOM for j in T_DOM]
A = [(i, j, k) for i in LR_DOM for j in LR_DOM for k in T_DOM]
for i in reversed(range(len(A))):
    if A[i][0] == A[i][1]:
        A.pop(i)
A_i = list(range(len(A)))
S_i = list(range(len(S)))
Q = [[-random()]*len(A) for _ in range(len(S))]
E = [[0]*len(A) for _ in range(len(S))]


def epi_greedy(s):
    if random() < EPSILON:
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

# begin receive signal
def receive_human_feedback():
    if button.is_pressed():
        return -1
    else:
        return 0


def motors_reset(back):
    left_motor.run_at_speed(0)
    right_motor.run_at_speed(0)
    if back:
        tail_motor.run_at_speed(0)
    left_motor_prime.run_to_position(300)
    right_motor_prime.run_to_position(70)
    if back:
        tail_motor_prime.run_to_position(0, direction='shortest path')


def get_state(yaw, tail):
    t = -1
    y = 0

    if (tail > 100):
        t = 1
    if yaw < -WIDE_ANGLE:
        y = -2
    elif yaw > WIDE_ANGLE:
        y = 2
    elif yaw < -NARROW_ANGLE:
        y = -1
    elif yaw > NARROW_ANGLE:
        y = 1

    s = (y, t)
    return S.index(s)


def get_reward(yaw):
    return -exp(abs(yaw/180.0))+1


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
            yaw = hub.motion_sensor.get_yaw_angle()
            tail = tail_motor_prime.get_position()
            s = get_state(yaw, tail)
            a = epi_greedy(s)
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            new_yaw = hub.motion_sensor.get_yaw_angle()
            new_tail = tail_motor_prime.get_position()
            new_s = get_state(new_yaw, new_tail)
            r = get_reward(new_yaw)
            update_reward_history(step, s, a, new_s, r, new_yaw)
            emote(r)
            Q[s][a] += ALPHA*q_error(s, a, r, new_s)
            step += 1
        send_reward_history(episode)


def et_q_error(s, a, new_s, new_a, r):
    return r + GAMMA*Q[new_s][new_a] - Q[s][a]


def sarsa_lambda():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0

        yaw = hub.motion_sensor.get_yaw_angle()
        tail = tail_motor_prime.get_position()
        s = get_state(yaw, tail)
        a = epi_greedy(s)
        reset_reward_history()

        while step < EPISODE_LEN:
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            new_yaw = hub.motion_sensor.get_yaw_angle()
            new_tail = tail_motor_prime.get_position()
            new_s = get_state(new_yaw, new_tail)
            new_a = epi_greedy(new_s)
            r = get_reward(new_yaw)
            update_reward_history(step, s, new_a, new_s, r, new_yaw)
            emote(r)
            delta = et_q_error(s, a, new_s, new_a, r)
            E[s][a] += 1
            for each_s in S_i:
                for each_a in A_i:
                    Q[each_s][each_a] += ALPHA * delta * E[each_s][each_a]
                    E[each_s][each_a] = GAMMA * LAMBDA * E[each_s][each_a]
            s = new_s
            a = new_a
            step += 1
        send_reward_history()

def sarsa_lambda_hf():
    while True:
        motors_reset(True)
        hub.left_button.wait_until_pressed()
        hub.motion_sensor.reset_yaw_angle()
        step = 0

        yaw = hub.motion_sensor.get_yaw_angle()
        tail = tail_motor_prime.get_position()
        s = get_state(yaw, tail)
        a = epi_greedy(s)
        reset_reward_history()

        while step < EPISODE_LEN:
            do_action(A[a])
            wait_for_seconds(INTERVAL)
            new_yaw = hub.motion_sensor.get_yaw_angle()
            new_tail = tail_motor_prime.get_position()
            new_s = get_state(new_yaw, new_tail)
            new_a = epi_greedy(new_s)
<<<<<<< HEAD
            r = get_reward_hf(new_yaw)
            update_reward_history(step, s, new_a, new_s, r, new_yaw)
            emote(r)
=======
            r = get_reward(new_yaw)
            dist = distance.get_distance_cm()
            if dist and dist < 50:
                r += -1
                hub.light_matrix.show_image('NO')
            else:
                emote(r)
>>>>>>> 85559214721854d5d7bb2eb88826c51973e7f5ff
            delta = et_q_error(s, a, new_s, new_a, r)
            E[s][a] += 1
            for each_s in S_i:
                for each_a in A_i:
                    Q[each_s][each_a] += ALPHA * delta * E[each_s][each_a]
                    E[each_s][each_a] = GAMMA * LAMBDA * E[each_s][each_a]
            s = new_s
            a = new_a
            step += 1
        send_reward_history()


# Q_learning()
# sarsa_lambda()
sarsa_lambda_hf()