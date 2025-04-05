# Generate two large prime numbers and their product

import random

def is_prime(n, k=5):  # Number of tests for Rabin-Miller primality test
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Find r and s
    r, s = 0, n - 1
    while s % 2 == 0:
        r += 1
        s //= 2

    # Witness loop
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_large_prime(bits):
    while True:
        # Generate a random number with the specified number of bits
        num = random.getrandbits(bits)
        # Ensure the number is odd
        num |= 1
        if is_prime(num):
            return num

# Generate two large prime numbers
bits = 16  # Number of bits for the prime numbers
prime1 = generate_large_prime(bits)
prime2 = generate_large_prime(bits)
n = prime1 * prime2

print("Large Prime 1:", prime1)
print("Large Prime 2:", prime2)
print("Product of Primes (n):", n)

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

# Find a base that is coprime with n
for x in range(2, n):
    if gcd(x,n)==1:
        print("base:", x)
        break
