# Symmetric Encryption Algorithms

1. Caesar cipher.

2. Des cipher

3. Triple Des cipher

4. Playfair Cipher

# Asymmetric Encryption Algorithms

1. RSA

2. DH

# Usage

this program was coded on windows, if you use on Linux system, you should change some functions by yourself.

## For server

1. First run `ServerMID.py`, to make sure the server is ready. 

   ```shell
   python ServerMID.py
   ```

   When you run this server, server will read file called `setting.json`, user name and hash value of password were stored here, all default password are `hash("111")`

2. And click the start button to run server.

## For clients

run `client1_gui.py` and `client2_gui.py`, in fact, name it whatever you want, but make sure the client name is stored in `setting.json`.

1. Input the right username(default) and password(111) for log in. After two clients is online, you can click refresh button and the combobox to choose the friend you want to send message.Type message in second input box, and click send msg button to send this message.

2. Before sending file, you must choose you friend fist, there is some problem in `sendFile` function. and another error is encoding type, which decided by the file itself.

3. If client1 change the encryption mode or exchange mode, and client2 send message to client1, first client2 need to choose client1 again to refresh the certificate of client1. Or, you will see client1 receive a debug message.







