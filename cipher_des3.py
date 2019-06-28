import random

import cipher_des

d = cipher_des.des()


def encode(plain: str, keys: tuple, padding=True):
    assert len(keys) == 3
    assert len(keys[0]) == 8
    if padding:
        plain = addPadding(plain)
    return d.encode(d.decode(d.encode(plain, keys[0], padding=False), keys[1], padding=False), keys[2], padding=False)


def decode(cipher: str, keys: tuple, padding=True):
    assert len(keys) == 3
    assert len(keys[0]) == 8
    p = d.decode(d.encode(d.decode(cipher, keys[2], padding=False), keys[1], padding=False), keys[0], padding=False)
    if padding:
        p = removePadding(p)
    return p


def generate_key(seed=-1):
    if seed != -1:
        random.seed(seed)
    return cipher_des.generate_key(random.randint(0, 1000)), cipher_des.generate_key(
        random.randint(0, 1000)), cipher_des.generate_key(random.randint(0, 1000))


def addPadding(text):  # Add padding to the datas using PKCS5 spec.
    pad_len = 8 - (len(text) % 8)
    text += pad_len * chr(pad_len)
    return text


def removePadding(data):  # Remove the padding of the plain text (it assume there is padding)
    pad_len = ord(data[-1])
    return data[:-pad_len]


if __name__ == "__main__":
    text = "hello"
    keys = generate_key()
    print(keys)
    cipher = encode(text, keys)
    print(cipher)
    print(decode(cipher, keys))
