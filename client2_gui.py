import binascii
import datetime
import json
import os
import random
import socket
import threading
import time
import tkinter
from collections import defaultdict
from tkinter import filedialog, ttk, messagebox, Frame

import chardet
import cipher_caesar
import cipher_des
import cipher_des3
import cipher_dh
import cipher_playfair
import cipher_rsa
import cryptocommon
import md5hash


def tcp_msg():
    publish_certificate()
    while True:
        data = ck.recv(1024).decode()  # Information from server
        stream = json.loads(data)
        print(stream)
        if stream["type"] == "online_client":
            comboxlist_friend["values"] = stream["client_list"]
        elif stream["type"] == "rep_client":
            certificate_list[stream["client"]] = stream["certificate"]
        elif stream["type"] == "error":
            print(stream["info"])


def udp_msg():
    while True:
        data, friend_addr = client_msg.recvfrom(1024)  # Information from other client
        data = data.decode()
        stream = json.loads(data)
        print(stream)

        if stream["type"] == "sek_ask":
            """
            type:'sek_ask'
            target:'c2'
            from:'c1'
            alg:''(aes, des3, caesar, playfair)
            """
            alg = stream["alg"]
            while stream["from"] not in certificate_list.keys():  # wait for certificate
                askCert(stream["from"])
                time.sleep(0.3)
            friend_certificate = certificate_list[stream["from"]]
            friend_pbk = friend_certificate["pbk"]
            pbk_list[stream["from"]] = friend_pbk

            if alg == "caesar":
                key_cipher = cipher_rsa.encryption(my_sek_list[alg], friend_pbk[0], friend_pbk[1])
            elif alg == "des3":
                key0 = cipher_rsa.str_encryption(my_sek_list[alg][0], friend_pbk[0], friend_pbk[1])
                key1 = cipher_rsa.str_encryption(my_sek_list[alg][1], friend_pbk[0], friend_pbk[1])
                key2 = cipher_rsa.str_encryption(my_sek_list[alg][2], friend_pbk[0], friend_pbk[1])
                key_cipher = (key0, key1, key2)
            else:
                key_cipher = cipher_rsa.str_encryption(my_sek_list[alg], friend_pbk[0], friend_pbk[1])
            """
            type:'sek_rep'
            target:'c1'
            from:'c2'
            alg:''(aes,des3,caesar,playfair)
            key:[123,435,54356,4325435,98897986]由c1的公钥加密后得到的
            """
            resp = {"type": "sek_rep", "target": stream["from"], "from": euser.get(), "alg": alg, "key": key_cipher}
            client_msg.sendto(json.dumps(resp).encode(), friend_addr)
        elif stream["type"] == "sek_rep":
            """
            type:'sek_rep'
            target:'c1'
            from:'c2'
            alg:''(aes,des3,caesar,playfair)
            key:[123,435,54356,4325435,98897986]由c1的公钥加密后得到的
            """
            alg = stream["alg"]
            if alg == "caesar":
                keys_list[stream["from"]][alg] = cipher_rsa.decryption(stream["key"], pvk[0], pvk[1])
            elif alg == "des3":
                key0 = cipher_rsa.numlist_to_decryption_str(stream["key"][0], pvk[0], pvk[1])
                key1 = cipher_rsa.numlist_to_decryption_str(stream["key"][1], pvk[0], pvk[1])
                key2 = cipher_rsa.numlist_to_decryption_str(stream["key"][2], pvk[0], pvk[1])
                keys_list[stream["from"]][alg] = key0, key1, key2
            else:
                keys_list[stream["from"]][alg] = cipher_rsa.numlist_to_decryption_str(stream["key"], pvk[0], pvk[1])
        elif stream["type"] == "pak_ask":
            """
            type:"pak_ask"
            target:c2
            from:c1
            pak:34458
            p:192863
            """
            repPak(stream, friend_addr)
        elif stream["type"] == "pak_rep":
            dh_shared_key_list[stream["from"]] = cipher_dh.get_key(pvk_a, stream["pak"], p)
            print("receive key from ", stream["from"], ":", dh_shared_key_list[stream["from"]])
        elif stream["type"] == "chat":
            alg = stream["alg"]
            ex_mode = stream["ex_mode"]
            while stream["from"] not in certificate_list.keys():  # wait for certificate
                askCert(stream["from"])
                time.sleep(0.2)
            friend_certificate = certificate_list[stream["from"]]
            friend_pbk = friend_certificate["pbk"]
            pbk_list[stream["from"]] = friend_pbk
            if exchange_mode == "rsa":
                friend_pbk = friend_certificate["pbk"]
                pbk_list[stream["from"]] = friend_pbk
                """
                type:'chat'
                target:'c2'
                from:'c1'
                signature:'foef32097^&*(%%ewfj043'
                msg:'*&^&^%^$^%xdcidsnvc'  
                alg:
                """
                if alg == encryption_mode and ex_mode == exchange_mode:
                    signature = cipher_rsa.numlist_to_decryption_str(stream["signature"], friend_pbk[0], friend_pbk[1])
                    if signature == stream["msg"]:
                        if encryption_mode == "des":
                            msg = d.decode(stream["msg"], my_sek_list[encryption_mode])
                        elif encryption_mode == "des3":
                            msg = cipher_des3.decode(stream["msg"], my_sek_list[encryption_mode])
                        elif encryption_mode == "caesar":
                            msg = cipher_caesar.decode(stream["msg"], my_sek_list[encryption_mode])
                        else:
                            msg = cipher_playfair.decode(stream["msg"],
                                                         table=cipher_playfair.generate_table(
                                                             my_sek_list[encryption_mode]))

                        if update_on_receive:
                            text.insert(tkinter.INSERT, stream["from"] + ": " + msg + "\n")
                        else:
                            message_list[stream["from"]].append(msg)
                    else:
                        print("signature:", signature)
                        print("msg:", stream["msg"])
                else:
                    text.insert(tkinter.INSERT, stream["from"] +
                                " send msg using " + alg + "," + ex_mode + ", but you are using " + encryption_mode + "," + exchange_mode + "\n")
            else:  # dh mode

                if alg == encryption_mode and ex_mode == exchange_mode:
                    signature = cipher_rsa.numlist_to_decryption_str(stream["signature"], friend_pbk[0],
                                                                     friend_pbk[1])
                    if stream["msg"] == signature:
                        while stream["from"] not in dh_shared_key_list.keys():
                            __askPak__(stream["from"], tuple(friend_certificate["address"]))
                        if encryption_mode == "des3":
                            key_random = cipher_des3.generate_key(dh_shared_key_list[stream["from"]])
                            message = cipher_des3.decode(stream["msg"], key_random)
                        elif encryption_mode == "des":
                            key_random = cipher_des.generate_key(dh_shared_key_list[stream["from"]])
                            message = d.decode(stream["msg"], key_random)
                        elif encryption_mode == "caesar":
                            key_random = cipher_caesar.generate_key(dh_shared_key_list[stream["from"]])
                            message = cipher_caesar.decode(stream["msg"], key_random)
                        else:
                            key_random = cipher_playfair.generate_key(dh_shared_key_list[stream["from"]])
                            message = cipher_playfair.decode(stream["msg"], cipher_playfair.generate_table(key_random))
                        if update_on_receive:
                            text.insert(tkinter.INSERT,
                                        stream["from"] + ":" + message + '\n')  # Display on the information box
                        else:
                            message_list[stream["from"]].append(message)
                else:
                    text.insert(tkinter.INSERT, stream["from"] +
                                " send msg using " + alg + "," + ex_mode + ", but you are using " + encryption_mode + "," + exchange_mode + "\n")
        elif stream["type"] == "file":
            recvFile(stream["name"], stream["hash"], stream["encoding"], stream["sender"])


def resend_certificate():
    while True:
        time.sleep(540)
        certificate["valid_before"] = str(datetime.datetime.now() + datetime.timedelta(minutes=10))
        stream = {"type": "certificate", "certificate": certificate}
        ck.send(json.dumps(stream).encode())


def connectServer():
    global ck
    ipStr = eip.get()
    portStr = eport.get()
    userStr = euser.get()
    pwd = cryptocommon.bytelist_to_hexstr(md5hash.hash(cryptocommon.asciistr_to_bytelist(epwd.get())))
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((ipStr, int(portStr)))  #
        client.send((userStr + pwd).encode())
        data = client.recv(1024).decode()
        print(data)
        if data == "error":
            messagebox.showerror("ERROR", "Wrong account or password, please try again.")
            raise Exception
    except Exception:
        return
    ck = client
    t1 = threading.Thread(target=tcp_msg)
    t1.start()
    t2 = threading.Thread(target=udp_msg)
    t2.start()
    t3 = threading.Thread(target=resend_certificate)
    t3.start()
    chatRoom()


def publish_certificate():
    certificate["valid_before"] = str(datetime.datetime.now() + datetime.timedelta(minutes=10))
    stream = {"type": "certificate", "certificate": certificate}
    ck.send(json.dumps(stream).encode())


def sendMail():
    if ck is not None:
        friend = comboxlist_friend.get()
        while friend not in certificate_list.keys():  # wait for certificate
            time.sleep(0.5)
        friend_certificate = certificate_list[friend]
        if friend_certificate["valid_before"] < str(datetime.datetime.now()):
            text.insert(tkinter.INSERT, friend + '\' certificate is invalid.\n')
            askCert(friend)
            return
        friend_ex_mode = friend_certificate["ex_mode"]
        friend_address = tuple(friend_certificate["address"])
        friend_alg = friend_certificate["alg"]
        pbk_list[friend] = friend_certificate["pbk"]
        if friend_ex_mode == "rsa":
            # 得到了加密方式以及friend地址，然后根据拿到的公钥以及来和对方共享密钥
            # 密钥在接收端方生成，询问接收端对应密钥。接受后通过私钥来解除

            while friend not in keys_list.keys() or friend_alg not in keys_list[friend]:
                askSek(friend, friend_alg, friend_address)
                time.sleep(0.5)
            # 得到对方的key之后，开始传输消息

            if friend_alg == "des":
                cipher = d.encode(esend.get("0.0", "end").strip(), keys_list[friend][friend_alg])
            elif friend_alg == "des3":
                cipher = cipher_des3.encode(esend.get("0.0", "end").strip(), keys_list[friend][friend_alg])
            elif friend_alg == "caesar":
                cipher = cipher_caesar.encode(esend.get("0.0", "end").strip(), keys_list[friend][friend_alg])
            else:
                cipher = cipher_playfair.encode(esend.get("0.0", "end").strip(),
                                                table=cipher_playfair.generate_table(keys_list[friend][friend_alg]))

        else:  # dh

            while friend not in dh_shared_key_list.keys():
                askPak(friend, tuple(friend_certificate["address"]))
                print("ask in sendmail()")
                time.sleep(0.2)
            # dh_shared_key_list[friend]，根据friend_alg选择加密方式
            if friend_alg == "caesar":
                key_random = cipher_caesar.generate_key(dh_shared_key_list[friend])
                cipher = cipher_caesar.encode(esend.get("0.0", "end").strip(), key_random)
            elif friend_alg == "des3":
                key_random = cipher_des3.generate_key(dh_shared_key_list[friend])
                cipher = cipher_des3.encode(esend.get("0.0", "end").strip(), key_random)
            elif friend_alg == "des":
                key_random = cipher_des.generate_key(dh_shared_key_list[friend])
                cipher = d.encode(esend.get("0.0", "end").strip(), key_random)
            else:
                key_random = cipher_playfair.generate_key(dh_shared_key_list[friend])
                cipher = cipher_playfair.encode(esend.get("0.0", "end").strip(), table=cipher_playfair.generate_table(
                    key_random))
            print("生成的随机密钥", key_random)

        """
        type:'chat'
        target:'c2'
        from:'c1'
        signature:'foef32097^&*(%%ewfj043'
        msg:'*&^&^%^$^%xdcidsnvc'   
        """

        stream = {"type": "chat", "target": friend, "from": euser.get(), "msg": cipher, "alg": friend_alg,
                  "ex_mode": friend_ex_mode,
                  "signature": cipher_rsa.str_encryption(cipher, pvk[0], pvk[1])}
        client_msg.sendto(json.dumps(stream).encode(), friend_address)



    else:
        text.insert(tkinter.INSERT, "you are offline!!\n")


def askSek(client: str, alg: str, address):
    """
    type:'sek_ask'
    target:'c2'
    from:'c1'
    alg:''(aes, des3, caesar, playfair)
    """
    stream = {"type": "sek_ask", "target": client, "from": euser.get(), "alg": alg}
    client_msg.sendto(json.dumps(stream).encode(), address)


def quit():
    stream = {"type": "quit"}
    if ck is not None:
        ck.send(json.dumps(stream).encode())
    exit(0)


def askPak(target: str, address):
    # 公钥得到之后，生成pak
    """
    type:"pak_ask"
    target:c2
    from:c1
    pak:34458
    p:192863
    """
    stream = {"type": "pak_ask", "target": target, "from": euser.get(), "pak": pak_a, "p": p}
    client_msg.sendto(json.dumps(stream).encode(), address)


def __askPak__(target, address):
    # 公钥得到之后，生成pak
    """
    type:"pak_ask"
    target:c2
    from:c1
    pak:34458
    p:192863
    """
    stream = {"type": "pak_ask", "target": target, "from": euser.get(), "pak": pak_a, "p": p}
    client_msg.sendto(json.dumps(stream).encode(), address)

    data, address = client_msg.recvfrom(1024)
    data = data.decode()
    stream = json.loads(data)
    dh_shared_key_list[stream["from"]] = cipher_dh.get_key(pvk_a, stream["pak"], p)


def repPak(stream: dict, friend_addr):
    """
    type:"pak_rep"
    target:c1
    from:c2
    pak:45134
    """
    rep = {}
    rep["type"] = "pak_rep"
    rep["target"] = stream["from"]
    rep["from"] = euser.get()
    p = stream["p"]
    pak_a = stream["pak"]
    pvk_b = random.randint(0, p - 1)
    a = cipher_dh.primroot_last(p)
    # pak_b = get_pak(p, a, pvk_b)
    pak_b = cipher_dh.get_pak(p, a, pvk_b)
    rep["pak"] = pak_b
    client_msg.sendto(json.dumps(rep).encode(), friend_addr)
    # key_b = get_key(pvk_b, pak_a, p)
    dh_shared_key_list[stream["from"]] = cipher_dh.get_key(pvk_b, pak_a, p)
    print("Shared List:", dh_shared_key_list)


def refresh_encrypt_mode(*args):
    global encryption_mode
    encryption_mode = comboxlist_encrypt.get()
    certificate["alg"] = encryption_mode
    certificate["valid_before"] = str(datetime.datetime.now() + datetime.timedelta(minutes=10))
    stream = {"type": "certificate", "certificate": certificate}
    if ck is not None:
        ck.send(json.dumps(stream).encode())


def refresh_ex_mode(*args):
    global exchange_mode
    exchange_mode = comboxlist_ex.get()
    certificate["ex_mode"] = exchange_mode
    certificate["valid_before"] = str(datetime.datetime.now() + datetime.timedelta(minutes=10))
    stream = {"type": "certificate", "certificate": certificate}
    if ck is not None:
        ck.send(json.dumps(stream).encode())


def refresh_friend_list(*args):
    stream = {"type": "refresh"}
    if ck is not None:
        ck.send(json.dumps(stream).encode())


def askCert(args):
    if isinstance(args, tkinter.Event):
        stream = {"type": "ask_client", "client": comboxlist_friend.get()}
        ck.send(json.dumps(stream).encode())
    else:
        stream = {"type": "ask_client", "client": args}
        ck.send(json.dumps(stream).encode())


def logout(*args):
    global update_on_receive
    if update_on_receive:
        update_on_receive = False
        btn_lock.configure(text='   UNLOCK  ')
    else:
        update_on_receive = True
        btn_lock.configure(text='  LOCK  ')
        friend = comboxlist_friend.get()
        for msg in message_list[friend]:
            text.insert(tkinter.INSERT, friend+": "+msg + "\n")
        message_list[friend].clear()
        # should put record information of this client


def sendFile():
    friend_certificate = certificate_list[comboxlist_friend.get()]
    friend_address = tuple(friend_certificate["address"])
    file_path = filedialog.askopenfilename()
    file = open(file_path, 'rb')
    stext = file.read()
    hexstr = binascii.b2a_hex(stext)
    filebyte = cryptocommon.hexstr_to_bytelist(hexstr)
    hashbytelist = md5hash.hash(filebyte)
    hashhexstr = cryptocommon.bytelist_to_hexstr(hashbytelist)
    hashhexstr = cipher_rsa.str_encryption(hashhexstr, pvk[0], pvk[1])  # signature
    file_name = file_path.split("/")[-1]

    stream = {"type": "file", "name": file_name, "hash": hashhexstr, "encoding": chardet.detect(stext)["encoding"],
              "sender": euser.get()}
    client_msg.sendto(json.dumps(stream).encode(), friend_address)
    time.sleep(0.8)
    stext += b"__end__"
    epoch = len(stext) // buffer
    res = int(len(stext) - epoch * buffer)
    print("sending file::::")
    t = 0
    for i in range(epoch):
        t = i
        time.sleep(0.1)
        client_msg.sendto(stext[i * buffer: (i + 1) * buffer], friend_address)
    if res != 0:
        client_msg.sendto(stext[t * buffer:t * buffer + res], friend_address)


def recvFile(file_name: str, hash_code: str, encoding: str, fromer: str):
    mkdir(euser.get())
    btext = b''
    while True:
        data, addr = client_msg.recvfrom(buffer)
        btext += data
        if btext[-7:] == b"__end__":
            break
    btext = btext[:-7]

    hexstr = binascii.b2a_hex(btext)
    filebyte = cryptocommon.hexstr_to_bytelist(hexstr)
    hashbytelist = md5hash.hash(filebyte)
    while fromer not in certificate_list.keys():  # wait for certificate
        askCert(fromer)
        time.sleep(0.2)
    friend_certificate = certificate_list[fromer]
    friend_pbk = friend_certificate["pbk"]
    hash_decode = cipher_rsa.numlist_to_decryption_str(hash_code, friend_pbk[0], friend_pbk[1])
    hashhexstr = cryptocommon.bytelist_to_hexstr(hashbytelist)
    if hashhexstr == hash_decode:
        file = open(euser.get() + "\\" + file_name, 'w')
        file.write((btext).decode('gb18030'))
        file.close()
        text.insert(tkinter.INSERT, "you have received a file from "+fromer+"\n")
    else:
        text.insert(tkinter.INSERT, "received some broken files.\n")


def mkdir(path):
    path = path.strip()
    path = path.rstrip("\\")
    isExists = os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


def chatRoom():
    frameButton.destroy()
    frameInput.destroy()
    win.geometry("680x440+400+300")
    print(euser.get())
    win.title("CHAT ROOM of " + euser.get())
    frameChat.grid(row=0, column=0, sticky=tkinter.N)
    frameSetting.grid(row=0, column=1)
    return 0


def LogIN():
    if len(euser.get()) == 0 or len(epwd.get()) == 0 or len(eport.get()) == 0 or len(eip.get()) == 0:
        messagebox.showerror("ERROR", "Sorry, your input is invalid.")
    else:

        connectServer()


# The following is about the operation of the interface and global value
win = tkinter.Tk()
win.title("LOG IN")
win.geometry("+500+200")

frameInput = Frame(width=300, height=200)
frameButton = Frame(width=300, height=50)
frameInput.grid(row=0, column=0)
frameButton.grid(row=1, column=0)

labelUse = tkinter.Label(frameInput, text="USER NAME").grid(row=0, column=0)
euser = tkinter.Variable()
entryUser = tkinter.Entry(frameInput, textvariable=euser).grid(row=0, column=1)
euser.initialize(str(__file__).split("/")[-1][:-3])

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

btn_file = tkinter.Button(frameChat, text="SEND FILE", width=35, command=sendFile).grid(row=2, sticky=tkinter.W)
button_msg = tkinter.Button(frameChat, text="SEND MSG", width=35, command=sendMail).grid(row=2, sticky=tkinter.E)

# for settings
frameSetting = Frame(width=20, height=80, padx=10)

labelencrypt = tkinter.Label(frameSetting, text="ENCRYPTION").grid(row=0, column=0, sticky=tkinter.N)

comboxlist_encrypt = ttk.Combobox(frameSetting)  # 初始化
comboxlist_encrypt["values"] = ("des", "playfair", "des3", "caesar")
comboxlist_encrypt.current(0)  # 选择第一个
comboxlist_encrypt.bind("<<ComboboxSelected>>", refresh_encrypt_mode)  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
comboxlist_encrypt.grid(row=1, rowspan=2, column=0)

labelexchange = tkinter.Label(frameSetting, text="RSA|DH").grid(row=4, column=0)

comboxlist_ex = ttk.Combobox(frameSetting)  # 初始化
comboxlist_ex["values"] = ("rsa", "dh")
comboxlist_ex.current(0)  # 选择第一个
comboxlist_ex.bind("<<ComboboxSelected>>", refresh_ex_mode)  # 绑定事件,(下拉列表框被选中时，绑定go()函数)
comboxlist_ex.grid(row=5, column=0)

label_friend = tkinter.Label(frameSetting, text="RECEIVER").grid(row=6, column=0)
comboxlist_friend = ttk.Combobox(frameSetting)  # 初始化
comboxlist_friend.bind("<<ComboboxSelected>>", askCert)
comboxlist_friend.grid(row=7, column=0)

btn_refresh = tkinter.Button(frameSetting, text="  REFRESH  ", command=refresh_friend_list).grid(row=8, column=0)
btn_lock = tkinter.Button(frameSetting, text="  LOCK  ", width=20, command=logout)
btn_lock.grid(column=0, sticky=tkinter.S, pady=230)

pbk_list = {}
keys_list = defaultdict(dict)
shared_keys_list = defaultdict(dict)
dh_shared_key_list = {}

ck = None  # Used to store client information

(n, e, d) = cipher_rsa.keyGeneration(20)
pbk = (e, n)
pvk = (d, n)

encryption_mode = "des"
exchange_mode = "rsa"

p, a = cipher_dh.generate_key()
pvk_a = random.randint(0, p - 1)
pak_a = cipher_dh.get_pak(p, a, pvk_a)

client_msg = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ('localhost', 1034)
client_msg.bind(address)  # udp

certificate = {
    "pbk": pbk,
    "alg": encryption_mode,
    "hash": "md5",
    "ex_mode": exchange_mode,
    "valid_before": str(datetime.datetime.now() + datetime.timedelta(minutes=10)),
    "address": address
}
certificate_list = defaultdict(dict)
my_sek_list = {"caesar": cipher_caesar.generate_key(), "des": cipher_des.generate_key(),
               "des3": cipher_des3.generate_key(), "playfair": cipher_playfair.generate_key()}

d = cipher_des.des()

buffer = 4096

message_list = defaultdict(list)

update_on_receive = True

win.mainloop()
