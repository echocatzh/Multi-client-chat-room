import random

# we need 2 helper mappings, from letters to ints and the inverse
L2I = dict(
    zip("ABCDEFGHIJKLMNjklmnopqrstuvwxyz123456789OPQRSTUVWXYZabcdefghi+-)(*&^%$#@!~`?/><';:\"[]{}|\n ,", range(91)))
I2L = dict(
    zip(range(91), "ABCDEFGHIJKLMNjklmnopqrstuvwxyz123456789OPQRSTUVWXYZabcdefghi+-)(*&^%$#@!~`?/><';:\"[]{}|\n ,"))


def encode(plaintext, key=3):
    """
    encode the plain text using caesar cipher.

    :param plaintext:the text we want to encode.
    :param key:choose the key for caesar cipher.
    :return:encoded data.
    """
    cipherText = ''
    # upper() is to make sure the letter is in alphabet
    for v in plaintext:
        # convert the plain data.
        cipherText += I2L[(L2I[v] + key) % 91]
    return cipherText


def decode(ciphertext, key=3):
    """
    decode the plain text using caesar cipher.

    :param ciphertext:he text we want to decode.
    :param key:choose the key for caesar cipher.
    :return:plain text.
    """
    plainText = ''
    for c in ciphertext:
        plainText += I2L[(L2I[c] - key) % 91]
    return plainText


def generate_key(seed=-1):
    if seed != -1:
        random.seed(seed)
    return random.randint(0, 90)


if __name__ == "__main__":
    plaintext = "hello shirlim, how are you!"
    key = generate_key()
    # encrypt plain text
    ciphtext = encode(plaintext, key)
    print(ciphtext)
    # decrypt encoded data
    print(decode(ciphtext, key))
