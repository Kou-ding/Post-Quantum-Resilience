# The crypto library is unable to generate keys smaller than 1024 bits
# Thus a from scratch approach is needed

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

# Step 1: Bob generates RSA keys
bob_key = RSA.generate(1024)  # Generate a 1024-bit RSA key
bob_private_key = bob_key.export_key()
bob_public_key = bob_key.publickey().export_key()
print("Bob's Private Key (Decimal):", int.from_bytes(bob_private_key, byteorder='big'))
print("Bob's Public Key (Decimal):", int.from_bytes(bob_public_key, byteorder='big'))

# Step 2: Alice encrypts a message using Bob's public key
message = b"Hello, Bob!"
rsa_public_key = RSA.import_key(bob_public_key)
cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
encrypted_message = cipher_rsa.encrypt(message)

# Step 3: Bob decrypts the message using his private key
rsa_private_key = RSA.import_key(bob_private_key)
cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
decrypted_message = cipher_rsa.decrypt(encrypted_message)

print("Original Message:", message)
print("Encrypted Message:", encrypted_message)
print("Decrypted Message:", decrypted_message)
