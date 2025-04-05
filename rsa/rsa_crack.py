import math

# Step 1: Given public key
e = 5
n = 77  # We will try to factor this
cipher = 47

# Step 2: Factor n = p * q
def factor_n(n):
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return i, n // i
    return None, None

p, q = factor_n(n)
print(f"Factors of n: p = {p}, q = {q}")

# Step 3: Compute Euler's totient
phi = (p - 1) * (q - 1)
print(f"Euler's totient φ(n) = {phi}")

# Step 4: Compute modular inverse of e (i.e., private key d)
def modinv(a, m):
    # Extended Euclidean Algorithm
    r0, r1 = a, m
    s0, s1 = 1, 0
    while r1 != 0:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        s0, s1 = s1, s0 - q * s1
    return s0 % m

d = modinv(e, phi)
print(f"Private key d = {d}")

# Step 5: Decrypt the cipher
# message = cipher^d mod n
message = pow(cipher, d, n)
print(f"Decrypted message = {message}")
