import json
import socket
import threading
import tkinter
from collections import defaultdict

win = tkinter.Tk()  # Main window
win.title('Server')
win.geometry("800x600+200+20")
win.configure(bg="#FFFFF0")
users = {}  # user socket dicts
user_list = []
certificate_list = defaultdict(dict)


def run(ck, ca):
    global load_dict
    data = ck.recv(1024).decode()
    userName = data[0:-32]
    pwd = data[-32:]
    valid = False
    for user_dict in load_dict:
        if user_dict["username"] == userName and user_dict["password"] == pwd:
            valid = True
            break
    if valid:
        ck.send("ok".encode())
        user_list.append(userName)
        users[userName] = ck  # store user information

        # print(users)
        printStr = userName + " online\n"  # show state.
        if lock.acquire():
            text.config(state=tkinter.NORMAL)
            text.insert(tkinter.END, printStr)
            text.config(state=tkinter.DISABLED)
            lock.release()

        while True:
            data = ck.recv(1024).decode()
            stream = json.loads(data)
            if lock.acquire():
                text.config(state=tkinter.NORMAL)
                text.insert(tkinter.INSERT, data + '\n')  # Display in the information window
                text.config(state=tkinter.DISABLED)
                lock.release()
                if stream["type"] == "certificate":
                    certificate_list[userName] = stream["certificate"]
                    client_list = []
                    for user in user_list:
                        if user != userName:
                            client_list.append(user)
                    resp = {"type": "online_client", "client_list": client_list}
                    ck.send(json.dumps(resp).encode())
                elif stream["type"] == "ask_client":
                    if stream["client"] in user_list:
                        ck.send(
                            json.dumps({"type": "rep_client", "client": stream["client"],
                                        "certificate": certificate_list[stream["client"]]}).encode())
                    else:
                        ck.send(json.dumps({"type": "error", "info": "Cannot find this client"}).encode())
                elif stream["type"] == "refresh":
                    client_list = []
                    for user in user_list:
                        if user != userName:
                            client_list.append(user)
                    resp = {"type": "online_client", "client_list": client_list}
                    ck.send(json.dumps(resp).encode())
    else:
        ck.send("error".encode())


def start():
    ipStr = eip.get()  # Getting IP from the input
    # Get IP from the input and get the port from the input.
    # Note that the port can not be occupied when it is acquired (8080, 9876, etc.)
    portStr = eport.get()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ipStr, int(portStr)))
    server.listen(10)  # Set up listeners, and set the maximum number of connections
    printStr = "server started.\n"  # Whether the connection was successful
    text.config(state=tkinter.NORMAL)
    text.insert(tkinter.INSERT, printStr)  # Display in the information window
    text.config(state=tkinter.DISABLED)
    while True:  # Dead loops are used here because the simulated server is running all the time.
        ck, ca = server.accept()  # Accept information from the connected client
        # Where CA is a tuple of IP and port number, CK is about client information
        t = threading.Thread(target=run, args=(ck, ca))  # Each connection to a client opens a thread
        # The parameters of the afferent function in Thread function are also in tuple form.
        t.start()  #


def startSever():
    global load_dict
    s = threading.Thread(target=start)  # Enabling a thread to open the server
    with open("setting.json", 'r') as load_f:
        load_dict = json.load(load_f)
    s.start()  # Open threads



# The following is about the operation of the interface

load_dict = {}
labelIp = tkinter.Label(win, text='     ip', bg="#FFFFF0").grid(row=0, column=0)
labelPort = tkinter.Label(win, text=' port', bg="#FFFFF0").grid(row=1, column=0)
eip = tkinter.Variable()
eip.initialize("localhost")
eport = tkinter.Variable()
eport.initialize("8081")
entryIp = tkinter.Entry(win, textvariable=eip, bg="#FFFFF0").grid(row=0, column=1)
entryPort = tkinter.Entry(win, textvariable=eport, bg="#FFFFF0").grid(row=1, column=1)
button = tkinter.Button(win, text="start", command=startSever, bg="#FFFFF0", relief=tkinter.RAISED).grid(row=2,
                                                                                                         column=0)
text = tkinter.Text(win, height=40, width=90, bg="#FFFFF0", relief=tkinter.SOLID)
labeltext = tkinter.Label(win, text='console message', bg="#FFFFF0").grid(row=3, column=0)
text.grid(row=3, column=1)
text.config(state=tkinter.DISABLED)
lock = threading.Lock()
win.mainloop()
