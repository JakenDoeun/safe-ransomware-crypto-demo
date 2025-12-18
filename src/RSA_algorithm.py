from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import socketserver, struct, json

def generate_rsa_keypair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    public_key = private_key.public_key()
    return private_key, public_key

def serialize_key(key, is_private=False) -> bytes:
    if is_private:
        return key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    else:
        return key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

def encryption_rsa(public_key, message: bytes) -> bytes:
    
    ciphertext = public_key.encrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext


def decryption_rsa(private_key, ciphertext: bytes) -> bytes:
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

#testing purpose only
if __name__ == "__main__":
    message = b"Attack at dawn!"
    private_key, public_key = generate_rsa_keypair()
    pem_public = serialize_key(public_key)
    pem_private = serialize_key(private_key, is_private=True)

    print("Public Key:")
    print(pem_public.decode())
    print("Private Key:")
    print(pem_private.decode())
    ciphertext = encryption_rsa(public_key, message)
    print("Ciphertext:")
    print(ciphertext)