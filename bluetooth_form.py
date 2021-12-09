import time
from typing import Callable
import serial
from tkinter import font
import tkinter
from timeout import timeout
import errno

s = serial.Serial("/dev/tty.usbmodem3285358433381", 9600, timeout=1)
s.timeout = 1


window = tkinter.Tk()
window.title('Feedback')
window.geometry("300x200+10+10")
f = font.Font(size=24)


@timeout(seconds=1)
def send_msg(msg: str) -> str:
    result = ""
    s.write(msg.encode())
    while s.in_waiting:
        result += s.readline().decode('ascii')
    return result

def send(word: str) -> Callable[[], None]:
    def send_word():
        try:
            result = send_msg(word)
            print(result)
        except serial.serialutil.SerialException:
            print("timeout. connection reset.")
            s.close()
            s.open()
    return send_word


btn = tkinter.Button(window, text="Bad", fg='red', command=send('bad'))
btn.place(x=30, y=110)
btn = tkinter.Button(window, text="Good", fg='green', command=send('good'))
btn.place(x=30, y=140)

window.mainloop()

