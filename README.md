<div>
    <br >
    <br >
    <br >
    <br >
    <br >
    <br >
    <br >
    <br >
    <div><center><font size='20'>NWPU</font></center></div>
    <br >
    <HR style="border:8 double" color=#0000ff SIZE=10>
    <br >
    <div><center><font size='6'>《Network and Information Security》</font></center></div>
    <div><center><font size='4'>-- School of Software</font></center></div>
<br >
<br >
<br >
<br >
<br >
<br >
<div><center><font size='6'>Assignment 03</font></center></div>
<br >
<br >
<br >
<br >    
<br >
<br >
<br >
<br >
<br >
<table border=0 style="text-align:right">
      <tr>
    <th> </th>
          <td><strong>Class</strong>: &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp 14011601</td>
  </tr> 
  <tr>
    <th> </th>
      <td><strong>Student ID</strong>:&nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp &nbsp 2016303126</td>
  </tr>
  <tr>
    <th> </th>
      <td><strong>Name</strong>:&nbsp Shirlim Zhang</td>
  </tr>
  <tr>
    <th> </th>
      <td><strong>Major</strong>: &nbsp Software Engineering</td>
    </tr>
        </table>



<center><font size=30>Catalog</font></center>

- [Symmetric Encryption Algorithms](# Symmetric Encryption Algorithms)
- [Asymmetric Encryption Algorithms](# Asymmetric Encryption Algorithms)
- [Usage](# Usage)
  - [For server](# For server)
  - [For clients](# For clients)



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

   When you run this server, server will read file called `setting.json`, user name and hash value of password were stored here, all default password are `hash("123")`

2. And click the start button to run server.

## For clients

run `client1_gui.py` and `client2_gui.py`, in fact, name it whatever you want, but make sure the client name is stored in `setting.json`.

1. Input the right username(default) and password(111) for log in. After two clients is online, you can click refresh button and the combobox to choose the friend you want to send message.Type message in second input box, and click send msg button to send this message.

2. Before sending file, you must choose you friend fist, there is some problem in `sendFile` function. and another error is encoding type, which decided by the file itself.

3. If client1 change the encryption mode or exchange mode, and client2 send message to client1, first client2 need to choose client1 again to refresh the certificate of client1. Or, you will see client1 receive a debug message.







