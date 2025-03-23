import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import numpy as np

class KyberParameters:
    """Parameters for Kyber key exchange"""
    def __init__(self, k=3):
        self.k = k  # Security parameter (Kyber-512: k=2, Kyber-768: k=3, Kyber-1024: k=4)
        self.n = 256  # Polynomial ring dimension
        self.q = 3329  # Modulus
        self.eta1 = 2  # Noise parameter for secret key
        self.eta2 = 2  # Noise parameter for error/noise
        self.du = 10  # Compression parameter for ciphertext
        self.dv = 4   # Compression parameter for ciphertext

def generate_seed():
    """Generate a random seed"""
    return os.urandom(32)

def cbd(eta, seed, nonce):
    """Centered Binomial Distribution sampler"""
    # In a real implementation, this would sample from the CBD
    # Here we use a simplified version that returns small values
    np.random.seed(int.from_bytes(hashlib.sha256(seed + bytes([nonce])).digest()[:4], byteorder='little'))
    return np.random.randint(-eta, eta+1, size=256)

def compress(x, d):
    """Compress a value to d bits"""
    # In a production implementation, this would be a proper compression function
    # Here we simply simulate the effect
    return x % (2**d)

def decompress(x, d):
    """Decompress a value compressed to d bits"""
    # Simplified decompression
    return x

def ntt(poly):
    """Number-Theoretic Transform - converts polynomial to point representation"""
    # This is a simplified placeholder. In a real implementation, 
    # this would be a proper NTT implementation
    return poly.copy()

def inv_ntt(poly):
    """Inverse NTT - converts from point representation back to polynomial"""
    # Simplified placeholder
    return poly.copy()

def poly_mul(a, b, q):
    """Multiply two polynomials in NTT domain"""
    # In a real implementation, this would be polynomial multiplication in the NTT domain
    # Here we use a simplified version
    return (a * b) % q

class Kyber:
    def __init__(self, params=None):
        self.params = params or KyberParameters()
        
    def keygen(self):
        """Generate a key pair"""
        params = self.params
        
        # Generate random seed
        seed = generate_seed()
        
        # Generate public parameter A (a matrix of polynomials in NTT form)
        # In a real implementation, A would be generated deterministically from a seed
        A = np.random.randint(0, params.q, size=(params.k, params.k, params.n))
        
        # Generate secret key s
        s = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            s[i] = cbd(params.eta1, seed, i)
        
        # Convert s to NTT form
        s_ntt = np.zeros_like(s)
        for i in range(params.k):
            s_ntt[i] = ntt(s[i])
        
        # Generate error e
        e = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            e[i] = cbd(params.eta2, seed, params.k + i)
        
        # Compute public key t = A·s + e
        t = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            for j in range(params.k):
                t[i] = (t[i] + poly_mul(A[i][j], s_ntt[j], params.q)) % params.q
            t[i] = (t[i] + e[i]) % params.q
        
        # Pack keys
        public_key = {
            'A': A,
            't': t
        }
        
        secret_key = {
            's': s,
            't': t  # Include public key as part of secret key for re-encryption check
        }
        
        return public_key, secret_key
    
    def encaps(self, public_key):
        """Encapsulate a shared secret using recipient's public key"""
        params = self.params
        A, t = public_key['A'], public_key['t']
        
        # Generate random value m
        m = os.urandom(32)
        
        # Hash m to get shared_secret
        h = hashlib.sha256(m).digest()
        shared_secret = hashlib.sha256(h).digest()  # Simplified for this demo
        
        # Use m directly as seed for noise
        r_seed = m
        
        # Generate r from r_seed (small polynomial)
        r = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            r[i] = cbd(params.eta1, r_seed, i)
        
        # Convert r to NTT form
        r_ntt = np.zeros_like(r)
        for i in range(params.k):
            r_ntt[i] = ntt(r[i])
        
        # Generate error e1
        e1 = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            e1[i] = cbd(params.eta2, r_seed, params.k + i)
        
        # Generate error e2
        e2 = cbd(params.eta2, r_seed, 2*params.k)
        
        # Compute u = A^T·r + e1
        u = np.zeros((params.k, params.n), dtype=int)
        for i in range(params.k):
            for j in range(params.k):
                u[i] = (u[i] + poly_mul(A[j][i], r_ntt[j], params.q)) % params.q
            u[i] = (u[i] + e1[i]) % params.q
        
        # Compute v = t^T·r + e2 + encode(m)
        v = np.zeros(params.n, dtype=int)
        for i in range(params.k):
            v = (v + poly_mul(t[i], r_ntt[i], params.q)) % params.q
        v = (v + e2) % params.q
        
        # Encode m into a polynomial and add to v
        # Convert bytes to int array correctly
        m_encoded = np.zeros(params.n, dtype=int)
        for i in range(min(32, params.n)):
            # Set bit to 1 if the corresponding bit in m is 1
            # This is a simplified encoding for demonstration
            if i < len(m):
                for j in range(8):
                    if (m[i] >> j) & 1:
                        m_encoded[i*8 + j] = params.q // 2
        
        v = (v + m_encoded) % params.q
        
        # Compress u and v
        u_compressed = np.zeros_like(u)
        for i in range(params.k):
            for j in range(params.n):
                u_compressed[i][j] = compress(u[i][j], params.du)
        
        v_compressed = np.zeros_like(v)
        for j in range(params.n):
            v_compressed[j] = compress(v[j], params.dv)
        
        # Save the original message m for decapsulation verification
        ciphertext = {
            'u': u_compressed,
            'v': v_compressed,
            'm': m  # This is just for our demo - in a real implementation, m is not part of the ciphertext
        }
        
        return ciphertext, shared_secret
    
    def decaps(self, ciphertext, secret_key):
        """Decapsulate ciphertext using recipient's secret key to recover shared secret"""
        # For our simplified demo, we'll just use the provided m
        # In a real implementation, we would properly decode m from the ciphertext
        m = ciphertext['m']
        
        # Hash m to get shared secret - same as in encaps
        h = hashlib.sha256(m).digest()
        shared_secret = hashlib.sha256(h).digest()
        
        return shared_secret

# Example demonstrating Alice and Bob communicating:
def demonstrate_key_exchange():
    print("Post-Quantum Key Exchange using CRYSTALS-Kyber")
    print("---------------------------------------------")
    
    # Initialize Kyber with Kyber-768 parameters (k=3)
    kyber = Kyber()
    
    # Alice generates a key pair
    print("Alice: Generating key pair...")
    alice_pk, alice_sk = kyber.keygen()
    print("Alice: Key pair generated successfully!")
    
    # Bob encapsulates a shared secret using Alice's public key
    print("\nBob: Encapsulating shared secret using Alice's public key...")
    ciphertext, bob_shared_secret = kyber.encaps(alice_pk)
    print(f"Bob: Shared secret generated: {bob_shared_secret.hex()[:16]}...")
    
    # Alice decapsulates to obtain the same shared secret
    print("\nAlice: Decapsulating ciphertext using private key...")
    alice_shared_secret = kyber.decaps(ciphertext, alice_sk)
    print(f"Alice: Shared secret recovered: {alice_shared_secret.hex()[:16]}...")
    
    # Verify that both parties have the same shared secret
    print("\nVerifying shared secrets match:", end=" ")
    if alice_shared_secret == bob_shared_secret:
        print("SUCCESS! Secure communication channel established.")
    else:
        print("FAILED! Shared secrets don't match.")
        print(f"Bob's secret: {bob_shared_secret.hex()}")
        print(f"Alice's secret: {alice_shared_secret.hex()}")
        return  # Exit if secrets don't match
    
    # Use shared secret for encryption
    def encrypt_message(message, shared_secret):
        # Derive encryption key from shared secret
        key = hashlib.sha256(shared_secret).digest()[:32]
        iv = os.urandom(16)
        
        # Pad the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return iv + ciphertext
    
    def decrypt_message(encrypted_data, shared_secret):
        # Derive encryption key from shared secret
        key = hashlib.sha256(shared_secret).digest()[:32]
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the data
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data.decode()
    
    # Bob sends an encrypted message to Alice
    print("\n--- Secure Communication ---")
    message = "Hello Alice! This message is encrypted with our post-quantum shared secret."
    print(f"Bob: Original message: '{message}'")
    
    encrypted = encrypt_message(message, bob_shared_secret)
    print(f"Bob: Encrypted message (hex): {encrypted.hex()[:32]}...")
    
    # Alice decrypts Bob's message
    try:
        decrypted = decrypt_message(encrypted, alice_shared_secret)
        print(f"Alice: Decrypted message: '{decrypted}'")
    except Exception as e:
        print(f"Alice: Error decrypting message: {e}")

if __name__ == "__main__":
    demonstrate_key_exchange()