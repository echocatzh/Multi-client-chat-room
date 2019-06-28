import threading
import tkinter
from tkinter import Frame, ttk, messagebox

win = tkinter.Tk()
win.title("LOG IN")
win.geometry("+500+200")


def connectServer():
    pass


def chatRoom():
    frameButton.destroy()
    frameInput.destroy()
    win.geometry("680x440+400+300")
    print(euser.get())
    win.title("CHAT ROOM")
    frameChat.grid(row=0, column=0, sticky=tkinter.N)
    frameSetting.grid(row=0, column=1)





def LogIN():
    if len(euser.get()) == 0 or len(epwd.get()) == 0 or len(eport.get()) == 0 or len(eip.get()) == 0:
        messagebox.showerror("ERROR", "Sorry, your input is invalid.")
    else:
        t = threading.Thread(target=chatRoom)
        t.start()
        connectServer()


frameInput = Frame(width=300, height=200)
frameButton = Frame(width=300, height=50)
frameInput.grid(row=0, column=0)
frameButton.grid(row=1, column=0)

labelUse = tkinter.Label(frameInput, text="USER NAME").grid(row=0, column=0)
euser = tkinter.Variable()
entryUser = tkinter.Entry(frameInput, textvariable=euser).grid(row=0, column=1)
euser.initialize("SHIRLIM1")

label_pwd = tkinter.Label(frameInput, text="PASSWORD").grid(row=1, column=0)
epwd = tkinter.Variable()
entryUser = tkinter.Entry(frameInput, textvariable=epwd)
entryUser.grid(row=1, column=1)
entryUser['show'] = '*'

labelIp = tkinter.Label(frameInput, text="IP").grid(row=2, column=0)
eip = tkinter.Variable()
entryIp = tkinter.Entry(frameInput, textvariable=eip).grid(row=2, column=1)
eip.initialize("localhost")

labelPort = tkinter.Label(frameInput, text="PORT").grid(row=3, column=0)
eport = tkinter.Variable()
entryPort = tkinter.Entry(frameInput, textvariable=eport).grid(row=3, column=1)
eport.initialize("8081")

button_in = tkinter.Button(frameButton, text="  LOG   IN  ", command=LogIN).grid(row=0, column=0)
button_out = tkinter.Button(frameButton, text="     EXIT      ", command=win.quit).grid(row=0, column=1)

# 创建一个顶级菜单
frameChat = Frame(width=70, height=80)


text = tkinter.Text(frameChat, height=20, width=70)
text.grid(row=0, column=0)

esend = tkinter.Text(frameChat, height=10, width=70)
esend.grid(row=1, column=0)

btn_file = tkinter.Button(frameChat, text="SEND FILE", width=35).grid(row=2, sticky=tkinter.W)
button_msg = tkinter.Button(frameChat, text="SEND MSG", width=35).grid(row=2, sticky=tkinter.E)

# for settings
frameSetting = Frame(width=20, height=80, padx=10)


labelencrypt = tkinter.Label(frameSetting, text="ENCRYPTION").grid(row=0, column=0, sticky=tkinter.N)

comboxlist_encrypt = ttk.Combobox(frameSetting)  # 初始化
comboxlist_encrypt["values"] = ("des", "playfair", "des3", "caesar")
comboxlist_encrypt.current(0)  # 选择第一个
comboxlist_encrypt.grid(row=1, rowspan=2, column=0)

labelexchange = tkinter.Label(frameSetting, text="RSA|DH").grid(row=4, column=0)

comboxlist_ex = ttk.Combobox(frameSetting)  # 初始化
comboxlist_ex["values"] = ("rsa", "dh")
comboxlist_ex.current(0)  # 选择第一个
comboxlist_ex.bind("<<ComboboxSelected>>")  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
comboxlist_ex.grid(row=5, column=0)

label_friend = tkinter.Label(frameSetting, text="RECEIVER").grid(row=6, column=0)
comboxlist_friend = ttk.Combobox(frameSetting)  # 初始化
comboxlist_friend.bind("<<ComboboxSelected>>")
comboxlist_friend.grid(row=7, column=0)

btn_refresh = tkinter.Button(frameSetting, text="  REFRESH  ").grid(row=8, column=0)
btn_lock = tkinter.Button(frameSetting, text="  LOCK  ", width=20).grid(column=0, sticky=tkinter.S, pady=230)

win.mainloop()
