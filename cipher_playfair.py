# -*- coding: utf-8 -*-
import itertools
import random

alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz{:}~!\"#$\n%&\'<>*+,-./0123456789"


def chunker(seq, size):
    """
    yield two letters from plain text each time.

    :param seq:plain text
    :param size:in playfair cipher, using two.
    :return:two letters as a pair.
    """
    it = iter(seq)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            return
        yield chunk


def prepare_input(dirty, insert_key):
    """
    Prepare the plaintext by up-casing it
    and separating repeated letters with *

    :param dirty: input data
    :param insert_key: default is "AOX"
    :return:pre-processing data.
    """
    # upper() is to make sure the letter is in alphabet
    dirty = dirty.replace(' ', "BMW")
    dirty = ''.join([c for c in dirty])
    clean = ""

    for i in range(len(dirty) - 1):
        clean += dirty[i]

        # for same letter. insert a "*"
        if dirty[i] == dirty[i + 1]:
            clean += insert_key

    clean += dirty[-1]

    if len(clean) & 1:
        # if the clean str is odd, add a insert_key to make sure it is even.
        clean += insert_key

    return clean


def generate_table(key="MYSECRETKEY",
                   alphabet=alphabet):
    # to use a 9*9 table (m*n letters)
    # using a list instead of a '2d' array because it makes the math
    # for setting up the table and doing the actual encoding/decoding simpler
    table = []

    # copy key chars into the table if they are in alphabet ignoring duplicates
    for char in key:
        if char not in table and char in alphabet:
            table.append(char)

    # fill the rest of the table in with the remaining alphabet chars
    for char in alphabet:
        if char not in table:
            table.append(char)

    return table


def encode(plaintext, table, insert_key="AOX", row_num=9, col_num=9):
    plaintext = prepare_input(plaintext, insert_key)
    ciphertext = ""
    for char1, char2 in chunker(plaintext, 2):
        row1, col1 = divmod(table.index(char1), col_num)
        row2, col2 = divmod(table.index(char2), col_num)

        if row1 == row2:
            # row1 == row2, using their right neighbours.
            ciphertext += table[row1 * col_num + (col1 + 1) % col_num]
            ciphertext += table[row2 * col_num + (col2 + 1) % col_num]
        elif col1 == col2:
            # col1 == col2, using their below neighbours.
            ciphertext += table[((row1 + 1) % row_num) * col_num + col1]
            ciphertext += table[((row2 + 1) % row_num) * col_num + col2]
        else:  # rectangle, from top-right to down-left.
            ciphertext += table[row1 * col_num + col2]
            ciphertext += table[row2 * col_num + col1]

    return ciphertext


def decode(ciphertext, table, row_num=9, col_num=9):
    plaintext = ""

    for char1, char2 in chunker(ciphertext, 2):
        row1, col1 = divmod(table.index(char1), col_num)
        row2, col2 = divmod(table.index(char2), col_num)

        if row1 == row2:  # row1 == row2, using their left neighbours.
            plaintext += table[row1 * col_num + (col1 - 1) % col_num]
            plaintext += table[row2 * col_num + (col2 - 1) % col_num]
        elif col1 == col2:  # col1 == col2, using their top neighbours.
            plaintext += table[((row1 - 1) % row_num) * col_num + col1]
            plaintext += table[((row2 - 1) % row_num) * col_num + col2]
        else:  # rectangle,from down-left to top-right
            plaintext += table[row1 * col_num + col2]
            plaintext += table[row2 * col_num + col1]
    plaintext = plaintext.replace('BMW', ' ')
    plaintext = plaintext.replace('AOX', '')
    return plaintext


def generate_key(seed=-1):
    if seed != -1:
        random.seed(seed)
    # to generate key for playfair using ramdom way;
    nums = list(map(ord, alphabet))
    tmp = random.choices(nums, k=20)
    tmp_str = list(map(chr, tmp))
    key = ""
    for t in tmp_str:
        key += t
    return key


if __name__ == '__main__':
    # plainText = input("input plain text:")
    #
    # # encrypt the plain text
    # cipherText = encode(plainText)
    # print("cipherText:", cipherText)
    #
    # # decrypt the encoded text
    # decodetext = decode(cipherText)
    # print("decode text:", decodetext)
    table = generate_table('65EG,\n}ZxxvMjg$95skV')

    print(decode("qWhCNYmp", table))
