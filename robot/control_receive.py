# LEGO type:standard slot:5

from spike.control import wait_for_seconds, wait_until, Timer
from math import *
from spike import PrimeHub
import hub, utime


curr_hub = PrimeHub()

vcp = hub.BT_VCP(0)

while True:
    if vcp.isconnected():
        if vcp.any():
            hub.display.show(hub.Image.HAPPY)
            while vcp.any():
                line = vcp.readline()
                if line is not None:
                    line_decoded = line.decode("ascii")
                    vcp.write(("\nyou sent " + line_decoded + "\n").encode())
                else:
                    vcp.write(("\nyou sent None\n").encode())
        else:
            hub.display.show(hub.Image.PACMAN)
    else:
        hub.display.show(hub.Image.SAD)
        utime.sleep(0.1)
