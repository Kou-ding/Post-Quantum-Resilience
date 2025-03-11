import secrets
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

# Note: This is a simplified implementation for educational purposes
# Real implementations would use specialized libraries like liboqs or PQClean

class KyberParameters:
    """
    Simplified parameters for Kyber
    In practice, use a proper PQ cryptography library
    """
    def __init__(self, k=3):  # k=3 for Kyber-768 (NIST level 3 security)
        self.k = k
        self.n = 256
        self.q = 3329  # Prime modulus
        self.eta1 = 2
        self.eta2 = 2
        self.du = 10
        self.dv = 4
        
    def gen_a(self, seed):
        """Generate pseudorandom matrix A (simplified)"""
        # In practice, this uses SHAKE-128 and has a specific structure
        random_generator = hashlib.shake_128(seed)
        a_matrix = []
        for i in range(self.k):
            row = []
            for j in range(self.k):
                # Generate pseudorandom coefficients mod q
                coeffs = []
                bytes_needed = (self.n * 16) // 8  # 16 bits per coefficient
                random_bytes = random_generator.digest(bytes_needed)
                
                for l in range(0, bytes_needed, 2):
                    if l + 1 < bytes_needed:
                        val = (random_bytes[l] << 8) | random_bytes[l + 1]
                        coeffs.append(val % self.q)
                
                # Ensure we have n coefficients
                while len(coeffs) < self.n:
                    coeffs.append(0)
                
                row.append(coeffs)
            a_matrix.append(row)
        return a_matrix

class Person:
    def __init__(self, name, params=None):
        self.name = name
        self.params = params if params else KyberParameters()
        self.shared_secret = None
        self.encryption_key = None
    
    def generate_keypair(self):
        """Generate a Kyber keypair (simplified)"""
        # Generate random seed for A matrix
        self.seed = secrets.token_bytes(32)
        
        # Generate the public matrix A from the seed
        self.A = self.params.gen_a(self.seed)
        
        # Generate secret vector s with small coefficients
        self.s = self._gen_small_vector(self.params.eta1)
        
        # Generate error vector e with small coefficients
        self.e = self._gen_small_vector(self.params.eta2)
        
        # Compute public key t = A·s + e
        self.t = self._matrix_vector_mul(self.A, self.s)
        self._add_vectors(self.t, self.e)
        
        # Return public key (seed for A, vector t)
        self.public_key = (self.seed, self.t)
        self.private_key = self.s
        
        print(f"{self.name}'s keypair generated")
        return self.public_key

    def _gen_small_vector(self, eta):
        """Generate a vector with small coefficients (simplified)"""
        # In practice, this uses a binomial distribution centered at 0
        result = []
        for i in range(self.params.k):
            coeffs = []
            for j in range(self.params.n):
                # Values between -eta and eta
                val = secrets.randbelow(2*eta + 1) - eta
                coeffs.append(val % self.params.q)  # Ensure it's in the ring
            result.append(coeffs)
        return result
    
    def _matrix_vector_mul(self, matrix, vector):
        """Matrix-vector multiplication in the ring"""
        k = self.params.k
        n = self.params.n
        q = self.params.q
        
        result = []
        for i in range(k):
            row_result = [0] * n
            for j in range(k):
                # Polynomial multiplication (simplified)
                for l in range(n):
                    for m in range(n):
                        idx = (l + m) % n
                        row_result[idx] = (row_result[idx] + matrix[i][j][l] * vector[j][m]) % q
            result.append(row_result)
        return result
    
    def _add_vectors(self, vec1, vec2):
        """Add two vectors in place (vec1 += vec2)"""
        for i in range(len(vec1)):
            for j in range(len(vec1[i])):
                vec1[i][j] = (vec1[i][j] + vec2[i][j]) % self.params.q
    
    def encapsulate(self, recipient_public_key):
        """Encapsulate a shared secret to the recipient (simplified)"""
        # Unpack recipient's public key
        recipient_seed, recipient_t = recipient_public_key
        
        # Regenerate matrix A from recipient's seed
        A = self.params.gen_a(recipient_seed)
        
        # Generate random vector r with small coefficients
        r = self._gen_small_vector(self.params.eta1)
        
        # Generate error vectors e1, e2 with small coefficients
        e1 = self._gen_small_vector(self.params.eta2)
        e2 = self._gen_small_vector(self.params.eta2)
        
        # Compute u = A^T·r + e1
        A_transpose = self._transpose(A)
        u = self._matrix_vector_mul(A_transpose, r)
        self._add_vectors(u, e1)
        
        # Compute v = t^T·r + e2 + encode(m)
        # For simplicity, we'll use a random message m
        m = secrets.token_bytes(32)
        v_temp = self._vector_dot(recipient_t, r)
        for i in range(len(v_temp)):
            v_temp[i] = (v_temp[i] + e2[0][i]) % self.params.q
        
        # Encode the message (simplified)
        encoded_m = self._encode_message(m)
        v = [(v_temp[i] + encoded_m[i]) % self.params.q for i in range(len(v_temp))]
        
        # Derive shared secret from message
        self.shared_secret = hashlib.sha256(m).digest()
        self.encryption_key = self.shared_secret
        
        # The ciphertext is (u, v)
        ciphertext = (u, v)
        
        print(f"{self.name} encapsulated a shared secret")
        return ciphertext
    
    def decapsulate(self, ciphertext):
        """Decapsulate the shared secret from the ciphertext (simplified)"""
        # Unpack the ciphertext
        u, v = ciphertext
        
        # Compute s^T·u
        s_dot_u = self._vector_dot(self.s, u)
        
        # Subtract from v to get encode(m)
        encoded_m = [(v[i] - s_dot_u[i]) % self.params.q for i in range(len(v))]
        
        # Decode to get the message
        m = self._decode_message(encoded_m)
        
        # Derive the shared secret
        self.shared_secret = hashlib.sha256(m).digest()
        self.encryption_key = self.shared_secret
        
        print(f"{self.name} decapsulated the shared secret")
        return self.shared_secret
    
    def _transpose(self, matrix):
        """Transpose a matrix"""
        k = self.params.k
        result = []
        for i in range(k):
            row = []
            for j in range(k):
                row.append(matrix[j][i])
            result.append(row)
        return result
    
    def _vector_dot(self, vec1, vec2):
        """Compute dot product of two vectors"""
        k = self.params.k
        n = self.params.n
        q = self.params.q
        
        result = [0] * n
        for i in range(k):
            for l in range(n):
                for m in range(n):
                    idx = (l + m) % n
                    result[idx] = (result[idx] + vec1[i][l] * vec2[i][m]) % q
        return result
    
    def _encode_message(self, message):
        """Encode a message into polynomial coefficients (simplified)"""
        result = [0] * self.params.n
        hash_value = hashlib.shake_256(message).digest(self.params.n)
        
        for i in range(min(len(hash_value), self.params.n)):
            # Scale to approximately q/2 for binary encoding
            result[i] = (hash_value[i] * (self.params.q // 256)) % self.params.q
        
        return result
    
    def _decode_message(self, encoded):
        """Decode polynomial coefficients back to message (simplified)"""
        # This is highly simplified - real implementation would use proper decoding
        # and error correction
        result = bytearray(self.params.n)
        for i in range(self.params.n):
            # Determine if coefficient is closer to 0 or q/2
            if encoded[i] > self.params.q // 4 and encoded[i] < 3 * self.params.q // 4:
                result[i] = 1
            else:
                result[i] = 0
        
        # Hash the decoded bits to get the original message
        return hashlib.shake_256(result).digest(32)
    
    def encrypt_message(self, message):
        """Encrypt a message using the shared secret"""
        if not self.shared_secret:
            raise ValueError("Shared secret not established yet")
        
        # Pad the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        # Generate a random IV
        iv = os.urandom(16)
        
        # Encrypt the message using AES-GCM which provides authentication
        cipher = Cipher(algorithms.AES(self.encryption_key), modes.GCM(iv), 
                       backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {'iv': iv, 'ciphertext': ciphertext, 'tag': encryptor.tag}
    
    def decrypt_message(self, encrypted_data):
        """Decrypt a message using the shared secret"""
        if not self.shared_secret:
            raise ValueError("Shared secret not established yet")
        
        # Extract the IV, ciphertext, and authentication tag
        iv = encrypted_data['iv']
        ciphertext = encrypted_data['ciphertext']
        tag = encrypted_data['tag']
        
        # Decrypt the message
        cipher = Cipher(algorithms.AES(self.encryption_key), 
                       modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the message
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode()

# Simulate Signal's double ratchet approach with Kyber for quantum resistance
class SignalStyleSession:
    def __init__(self, person):
        self.person = person
        self.message_keys = {}
        self.current_sending_key = None
        self.current_receiving_key = None
        self.message_number = 0
    
    def derive_message_key(self, shared_secret, message_number):
        """Derive a message key from shared secret and message number"""
        key_material = shared_secret + message_number.to_bytes(4, byteorder='big')
        return hashlib.sha256(key_material).digest()
    
    def encrypt_message(self, message, recipient_session):
        """Encrypt a message for a recipient using the double ratchet protocol"""
        # Get the current sending key
        if not self.current_sending_key:
            raise ValueError("No sending key established")
        
        # Derive a message key
        message_key = self.derive_message_key(self.current_sending_key, self.message_number)
        
        # Encrypt the message
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message.encode()) + padder.finalize()
        
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(message_key), modes.GCM(iv), 
                       backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        encrypted = {
            'iv': iv,
            'ciphertext': ciphertext,
            'tag': encryptor.tag,
            'message_number': self.message_number
        }
        
        # Increment the message number
        self.message_number += 1
        
        return encrypted
    
    def decrypt_message(self, encrypted_data):
        """Decrypt a message using the double ratchet protocol"""
        # Get the message number
        message_number = encrypted_data['message_number']
        
        # Derive the message key
        if not self.current_receiving_key:
            raise ValueError("No receiving key established")
        
        message_key = self.derive_message_key(self.current_receiving_key, message_number)
        
        # Decrypt the message
        iv = encrypted_data['iv']
        ciphertext = encrypted_data['ciphertext']
        tag = encrypted_data['tag']
        
        cipher = Cipher(algorithms.AES(message_key), modes.GCM(iv, tag), 
                       backend=default_backend())
        decryptor = cipher.decryptor()
        padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Unpad the message
        unpadder = padding.PKCS7(128).unpadder()
        plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
        
        return plaintext.decode()

# Demonstration
if __name__ == "__main__":
    print("Initializing quantum-resistant Signal-style communication...")
    
    # Create Alice and Bob
    alice = Person("Alice")
    bob = Person("Bob")
    
    # Generate keypairs
    alice_public_key = alice.generate_keypair()
    bob_public_key = bob.generate_keypair()
    
    print("\n--- Initial Key Exchange ---")
    # Alice encapsulates a shared secret to Bob
    ciphertext = alice.encapsulate(bob_public_key)
    
    # Bob decapsulates to get the same shared secret
    bob.decapsulate(ciphertext)
    
    # Verify shared secrets match
    alice_secret_hex = alice.shared_secret.hex()[:10] + "..."
    bob_secret_hex = bob.shared_secret.hex()[:10] + "..."
    print(f"Alice's shared secret: {alice_secret_hex}")
    print(f"Bob's shared secret: {bob_secret_hex}")
    print(f"Shared secrets match: {alice.shared_secret == bob.shared_secret}")
    
    # Create Signal-style sessions
    alice_session = SignalStyleSession(alice)
    bob_session = SignalStyleSession(bob)
    
    # Initialize session keys
    alice_session.current_sending_key = alice.shared_secret
    alice_session.current_receiving_key = alice.shared_secret
    bob_session.current_sending_key = bob.shared_secret
    bob_session.current_receiving_key = bob.shared_secret
    
    print("\n--- Secure Communication ---")
    # Alice sends a message to Bob
    message = "Hello Bob, this is a quantum-resistant message from Alice!"
    encrypted = alice_session.encrypt_message(message, bob_session)
    print(f"Alice → Bob: {message}")
    
    # Bob decrypts Alice's message
    decrypted = bob_session.decrypt_message(encrypted)
    print(f"Bob decrypted: {decrypted}")
    
    # Bob sends a response to Alice
    response = "Hi Alice, I received your quantum-resistant message safely!"
    encrypted_response = bob_session.encrypt_message(response, alice_session)
    print(f"Bob → Alice: {response}")
    
    # Alice decrypts Bob's response
    decrypted_response = alice_session.decrypt_message(encrypted_response)
    print(f"Alice decrypted: {decrypted_response}")