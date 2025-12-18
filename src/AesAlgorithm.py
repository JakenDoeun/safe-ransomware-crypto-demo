import os
import time
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher

def encrypt_file(file_path, key):
    iv = os.urandom(16)

    cipher_txt = Cipher(algorithms.AES(key), modes.CTR(iv)) #create cipher object (set algorithm and mode)
    encryptor = cipher_txt.encryptor() #create encryptor object from cipher (used to perform encryption)

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    #feed data to encryptor and end finalize encryption
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    #write back the encrypted data to file
    with open(file_path, 'wb') as f:
        f.write(iv + ciphertext) 


def decrypt_file(file_path, key): 
    with open(file_path, 'rb') as f:
        data = f.read()

    iv = data[:16]
    ciphertext = data[16:]

    cipher_txt = Cipher(algorithms.AES(key), modes.CTR(iv))
    decryptor = cipher_txt.decryptor()

    #feed data to decryptor and end finalize decryption
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    #write back the decrypted data to file
    with open(file_path, 'wb') as f:
        f.write(plaintext)

#for testing purpose only
if __name__ == "__main__":
    key = os.urandom(32) 

    print(f'Generated Key: {key.hex()}')
    time.sleep(2)

    
    file_to_encrypt = '/home/k4k/vscode/safe-ransomware-crypto-demo/src/testing_env/file1.txt'
    encrypt_file(file_to_encrypt, key)
    print(f'File: {file_to_encrypt} encrypted.')

    for _ in range(5):
        print(f'Decrypting file in {5 - _} seconds...')
        time.sleep(1)

    key_input = input('Enter the decryption key (hex format): ')
    Vkey = bytes.fromhex(key_input.strip())

    decrypt_file(file_to_encrypt, Vkey)
    print(f'File: {file_to_encrypt} decrypted.')

