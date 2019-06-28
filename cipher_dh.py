import random


def fastExpMod(b, e, m):
    """
    e = e0*(2^0) + e1*(2^1) + e2*(2^2) + ... + en * (2^n)

    b^e = b^(e0*(2^0) + e1*(2^1) + e2*(2^2) + ... + en * (2^n))
        = b^(e0*(2^0)) * b^(e1*(2^1)) * b^(e2*(2^2)) * ... * b^(en*(2^n))

    b^e mod m = ((b^(e0*(2^0)) mod m) * (b^(e1*(2^1)) mod m) * (b^(e2*(2^2)) mod m) * ... * (b^(en*(2^n)) mod m) mod m
    """
    result = 1
    while e != 0:
        if (e & 1) == 1:
            # ei = 1, then mul
            result = (result * b) % m
        e >>= 1
        # b, b^2, b^4, b^8, ... , b^(2^n)
        b = (b * b) % m
    return result


def primeTest(n):
    q = n - 1
    k = 0
    # Find k, q, satisfied 2^k * q = n - 1
    while q % 2 == 0:
        k += 1
        q //= 2
    a = random.randint(2, n - 2)
    # If a^q mod n= 1, n maybe is a prime number
    if fastExpMod(a, q, n) == 1:
        return "inconclusive"
    # If there exists j satisfy a ^ ((2 ^ j) * q) mod n == n-1, n maybe is a prime number
    for j in range(0, k):
        if fastExpMod(a, (2 ** j) * q, n) == n - 1:
            return "inconclusive"
    # a is not a prime number
    return "composite"


def findPrime(halfkeyLength):
    while True:
        # Select a random number n
        n = random.randint(100, 1 << halfkeyLength)
        if n % 2 != 0:
            found = True
            # If n satisfy primeTest 10 times, then n should be a prime number
            for i in range(0, 10):
                if primeTest(n) == "composite":
                    found = False
                    break
            if found:
                return n


def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a


def primroot_last(modulo):
    roots = []
    required_set = set(num for num in range(1, modulo) if gcd(num, modulo) == 1)

    for g in range(1, modulo):
        actual_set = set(pow(g, powers) % modulo for powers in range(1, modulo))
        if required_set == actual_set:
            roots.append(g)
    return roots[-1]


def get_pak(p, a, X):
    return (a ** X) % p


def get_key(X, Y, p):
    return (Y ** X) % p


def generate_key(seed=-1):
    if seed != -1:
        random.seed(seed)
    p = findPrime(8)
    a = primroot_last(p)
    return p, a


if __name__ == "__main__":
    p = findPrime(8)
    a = primroot_last(p)

    pvk_a = random.randint(0, p - 1)
    pvk_b = random.randint(0, p - 1)

    pak_a = get_pak(p, a, pvk_a)
    pak_b = get_pak(p, a, pvk_b)

    key_a = get_key(pvk_a, pak_b, p)
    key_b = get_key(pvk_b, pak_a, p)
    print(key_a)
    print(key_a == key_b)
