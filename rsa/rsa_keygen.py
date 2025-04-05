# Generate RSA keypair
import random

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def modinv(a, m):
    m0, x0, x1 = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def generate_keypair(p, q):
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(2, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)

    # Compute the modular inverse of e with respect to phi to get d
    d = modinv(e, phi)

    # Return public and private keypair
    return ((e, n), (d, n))

# Example usage with small primes
p = 61
q = 53
public_key, private_key = generate_keypair(p, q)

print("Public Key (e, n):", public_key)
print("Private Key (d, n):", private_key)
