# Lego Spike RL Silly-Walk

By Yichen Wei, Tianyi Ma and Jonathan Liu.

# File Structure:
```
.
├── README.md       - This file
├── analyze.ipynb   - The python notebook used to generate the graph and analyze
├── bluetooth_ctl.py      - Command line bluetooth serial control (unused)
├── bluetooth_form.py     - Form-based bluetooth serial control
├── data            - Data folder
│   ├── __init__.py
│   ├── hl1.py            - data from human interaction
│   ├── qlearning.py      - data from q learning
│   └── sarsa_lam1.py     - data fro sarsa lambda (eligibility trace)
├── robot           - code for the robot
│   ├── control_receive.py  - test of the bluetooth serial function (unused)
│   ├── main-algo.py        - main implementation of three algorithms
│   └── sillywalk1-robot.py - test of the bluetooth serial function (unused)
└── timeout.py      - unused, for serial connection timeout
```

## How-tos
### How to Download the program:
On the computer,
- Download [LEGO Spike software](https://education.lego.com/en-us/downloads/spike-app/software). 
- Connect to the robot using the software.
- Start a new project. Copy content of `robot/main-algo.py` into the project.
- Scroll to the bottom of the file. comment/uncomment the algorithm to run as
desired.
- Download the code onto the robot.

### How to run the robot
- Start the program.
- Press the left button to start each episode.
- If running the human-interaction algorithm, quickly wave at the 
proximity sensor of the robot after the timestep if you think 
the robot is doing something wrong. The robot will display
a "X" on its led matrix to show that it has received your feedback.
- At the end of an episode, the yaw angle and reward history of the whole 
episode will be send back to the debug serial port that can be viewed
in the SPIKE app in the console area.

## Video Demonstration:
[Go to google Drive](https://drive.google.com/drive/folders/1Ye4T9prcPms3T2SMyC9DWFNtjF662NIt?usp=sharing)
