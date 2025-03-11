import random
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def is_prime(n):
    """Check if a number is prime"""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def find_primitive_root(p):
    """Find a primitive root modulo p"""
    if not is_prime(p):
        raise ValueError("Number must be prime")
    
    # Find a primitive root
    for g in range(2, p):
        # Check if g is a primitive root
        used = set()
        for i in range(1, p):
            val = pow(g, i, p)
            if val in used:
                break
            used.add(val)
        if len(used) == p - 1:
            return g
    return None

class Person:
    def __init__(self, name, p, g):
        self.name = name
        self.p = p  # A large prime number (public)
        self.g = g  # A primitive root modulo p (public)
        self.private_key = random.randint(1, p-2)  # Private key
        self.public_key = pow(g, self.private_key, p)  # Public key
        self.shared_secret = None
    
    def generate_shared_secret(self, other_public_key):
        """Generate the shared secret using the other person's public key"""
        self.shared_secret = pow(other_public_key, self.private_key, self.p)
        # Convert to a key suitable for encryption
        self.encryption_key = hashlib.sha256(str(self.shared_secret).encode()).digest()
        print(f"{self.name}'s shared secret: {self.shared_secret}")
        print(f"{self.name}'s encryption key: {self.encryption_key.hex()}")
        return self.shared_secret
    
    def encrypt_message(self, message):
        """Encrypt a message using the shared secret"""
        if not self.shared_secret:
            raise ValueError("Shared secret not established yet")
        
        # Pad the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Encrypt the message
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {'iv': iv, 'ciphertext': ciphertext}
    
    def decrypt_message(self, encrypted_data):
        """Decrypt a message using the shared secret"""
        if not self.shared_secret:
            raise ValueError("Shared secret not established yet")
        
        # Extract the IV and ciphertext
        iv = encrypted_data['iv']
        ciphertext = encrypted_data['ciphertext']
        
        # Decrypt the message
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the message
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode()

# Demonstration
if __name__ == "__main__":
    # Choose a large prime number and a primitive root
    p = 23  # In practice, use a much larger prime
    g = find_primitive_root(p)
    
    print(f"Public parameters: p={p}, g={g}")
    
    # Create Alice and Bob
    alice = Person("Alice", p, g)
    bob = Person("Bob", p, g)
    
    print(f"Alice's private key: {alice.private_key}")
    print(f"Alice's public key: {alice.public_key}")
    print(f"Bob's private key: {bob.private_key}")
    print(f"Bob's public key: {bob.public_key}")
    
    # Exchange public keys and generate shared secrets
    alice.generate_shared_secret(bob.public_key)
    bob.generate_shared_secret(alice.public_key)
    
    # Verify that both parties have the same shared secret
    print(f"Shared secrets match: {alice.shared_secret == bob.shared_secret}")
    
    # Alice encrypts a message for Bob
    message = "Hello Bob, this is a secret message from Alice!"
    encrypted = alice.encrypt_message(message)
    print(f"Alice's encrypted message: {encrypted['ciphertext'].hex()}")
    
    # Bob decrypts Alice's message
    decrypted = bob.decrypt_message(encrypted)
    print(f"Bob decrypted: {decrypted}")
    
    # Bob sends a response to Alice
    response = "Hi Alice, I received your secret message!"
    encrypted_response = bob.encrypt_message(response)
    print(f"Bob's encrypted response: {encrypted_response['ciphertext'].hex()}")
    
    # Alice decrypts Bob's response
    decrypted_response = alice.decrypt_message(encrypted_response)
    print(f"Alice decrypted: {decrypted_response}")