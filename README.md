# Educational Mini Ransomware Demo

An educational cryptography project written in Python that demonstrateshow ransomware uses cryptography to encrypt a victim’s data. The project focuses on the most common approach: hybrid encryption, which combines symmetric and asymmetric cryptographic techniques.

This project is intended to be executed in a controlled and ethical
environment, such as a virtual machine.

**NOTE:** This project is built strictly for cybersecurity learning purposes.

## Project Overview

This project was created to explore and understand the basics of
ransomware, including its common cryptographic algorithms, workflows,
and design logic. The primary focus is on cryptography concepts rather
than malware behavior.

Through this demo, cybersecurity students can gain practical insight
into ransomware-related encryption workflows, key management complexity
(even at a basic level), and analytical thinking when studying real-world
attack techniques.

> A strong defender understands how attackers think.
> — Defensive security principle

## Features

- Demonstrates hybrid encryption using AES for file encryption and RSA for secure key exchange
- Simulates ransomware-style encryption with a controlled decryption workflow
- Implements client–server communication for centralized encryption key management
- Uses unique client identifiers (UUID) to ensure per-client encryption authorization
- Detects file paths dynamically based on the host operating system (OS)
- Supports a manually authorized decryption process

## How It Works

1. On  client-side generates a random symmetric key for file encryption.
2. Target files are encrypted locally on victim's device using the symmetric key (AES).
3. The symmetric key is encrypted using the server’s public key (RSA).
4. The encrypted key and client identifier are sent to the server.
5. The server stores encryption metadata and manages decryption authorization.
6. The symmetric key is displayed on server's terminal when authorized, And it sent to the client for decryption via other channel or methon.
7. The UUID on server's JSON will be delete after decrypted succeeful

## Tech Stack

- Python 3.13+
- Project used dependencies listed in the `requirements.txt` file
- Symmetric encryption: AES
- Asymmetric encryption: RSA
- Socket-based client–server communication
- JSON-based key and metadata storage
- Cross-platform execution (Windows, Linux)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JakenDoeun/mini-ransomware-crypto-demo.git
cd mini-ransomware-crypto-demo
```

2. Create the virtual environment for python:

```bash

python -m venv venv
source venv/bin/activate        # Linux
venv\Scripts\activate           # Windows
br
```

3. Install project denpendencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Server

Run the server script first. The server is responsible for key management
and decryption authorization.

```bash
python src/Server.py
```

2. Start the Client

   - without build .EXE

     ```bash
     python src/client.py
     ```
   - build .EXE (windows only)

     ```bash
     pyinstaller --onefile --windowed --add-data "src/sigma_cat.png;" src/Victim_GUI.py
     ```

## Ethical Notice

This project is for **educational and defensive cybersecurity purposes only**.
Do NOT deploy or modify this code for malicious use.

Any misuse of this project for malicious activities is strictly
prohibited. The author does not take responsibility for improper or
illegal use of this code.

## Contributing

Contributions are welcome for educational and defensive cybersecurity
purposes only. If you would like to improve this project, please ensure
that your changes align with the project’s ethical guidelines.

Suggested contributions include:

- Code refactoring and cleanup
- Documentation improvements
- Bug fixes and error handling
- Security-focused enhancements

Please submit changes via pull requests with a clear description of the
proposed improvement.

## Future Improvements

- Replace JSON-based key storage with the database solution
- Add secure key lifecycle management, including automatic key deletion after decryption
- Introduce structured logging and monitoring for security analysis
- Improve error handling and resilience in client–server communication
- Improve speed excution for .EXE file

## License

This project is licensed under the MIT License.
See the `LICENSE` file for more details.
