import time
import serial

s = serial.Serial("/dev/tty.usbmodem3285358433381", 9600, timeout=1)
s.timeout = 1

print("Bad = b, Good = g")

while True:
    #s.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode())
    msg = input(">>> ")
    s.write(msg.encode())
    while s.in_waiting:
        print(s.readline().decode('ascii'))
    print(s.out_waiting)
