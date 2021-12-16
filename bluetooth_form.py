import time
from typing import Callable
import serial
from tkinter import font
import tkinter
from timeout import timeout
import errno

s = serial.Serial("/dev/tty.LEGOHubMartinsHub", 115200, timeout=1)
s.timeout = 1


window = tkinter.Tk()
window.title('Feedback')
window.geometry("300x200+10+10")
f = font.Font(size=24)
textvar = tkinter.StringVar()
btn_enabled = tkinter.BooleanVar()
label = tkinter.Label(textvariable=textvar)
label.place(x=10, y=20)
textvar.set("1234")
btn_enabled.set(False)

@timeout(seconds=2)
def send_msg(msg: str) -> str:
    result = ""
    s.write(msg.encode())
    while s.in_waiting:
        result += s.readline().decode('ascii')
    return result

@timeout(seconds=2)
def find_in_stream(keyword):
    while s.in_waiting:
        w = s.readline().decode('ascii')
        print(w)
        if keyword in w:
            return True
    return False


btn_bad = tkinter.Button(window, text="Bad", fg='red')
btn_bad['state'] = 'normal'
btn_bad.place(x=30, y=110)
btn_good = tkinter.Button(window, text="Good", fg='green')
btn_good['state'] = 'normal'
btn_good.place(x=30, y=140)

def send(word: str) -> Callable[[], None]:
    global textvar
    def send_word():
        try:
            result = send_msg(word)
            print(result)
            for content in result.split('\n'):
                if "which have reward" in content:
                    textvar.set(content)
            # btn_good['state'] = 'disabled'
            # btn_bad['state'] = 'disabled'
        except serial.serialutil.SerialException:
            print("timeout. connection reset.")
            textvar.set("timeout...")
            s.close()
            s.open()
        window.after(500, check_if_ready)
    return send_word

btn_bad['command'] = send("bad")
btn_good['command'] = send("good")


def check_if_ready():
    try:
        if btn_bad['state'] != 'normal':
            print("00")
            if find_in_stream("ready"):
                # btn_bad['state'] = 'normal'
                # btn_good['state'] = 'normal'
                textvar.set('give your rating...')
        else:
            print("11")
            if find_in_stream("resuming operation"):
                pass
                # btn_bad['state'] = 'disabled'
                # btn_good['state'] = 'disabled'
    except:
        s.close()
        s.open()
    window.after(500, check_if_ready)

window.after(2000, check_if_ready)

window.mainloop()

