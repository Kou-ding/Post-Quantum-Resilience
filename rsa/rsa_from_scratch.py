# Bob Alice example
import random

def gcd(a, b):
    """Compute the greatest common divisor of a and b."""
    while b != 0:
        a, b = b, a % b
    return a

def modinv(a, m):
    """Return the modular inverse of a with respect to m using Extended Euclidean Algorithm."""
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
    """Generate a public/private keypair."""
    n = p * q
    phi = (p - 1) * (q - 1)

    # Choose an integer e such that e and phi(n) are coprime
    e = random.randrange(1, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(1, phi)

    # Use Extended Euclid's Algorithm to generate the private key
    d = modinv(e, phi)

    # Return public and private keypair
    return ((e, n), (d, n))

def encrypt(public_key, plaintext):
    """Encrypt the plaintext with the public key."""
    e, n = public_key
    cipher = [pow(ord(char), e, n) for char in plaintext]
    return cipher

def decrypt(private_key, ciphertext):
    """Decrypt the ciphertext with the private key."""
    d, n = private_key
    plain = [chr(pow(char, d, n)) for char in ciphertext]
    return ''.join(plain)

# Example usage
p = 61
q = 53
public, private = generate_keypair(p, q)

message = "Hello"
encrypted_msg = encrypt(public, message)
decrypted_msg = decrypt(private, encrypted_msg)

print("Original Message:", message)
print("Encrypted Message:", encrypted_msg)
print("Decrypted Message:", decrypted_msg)
