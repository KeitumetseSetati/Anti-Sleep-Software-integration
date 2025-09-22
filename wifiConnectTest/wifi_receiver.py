import socket
import json

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 12345    # Match the ESP32's udpPort

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print("Listening for UDP data on port", UDP_PORT)

while True:
    data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
    try:
        parsed = json.loads(data.decode('utf-8'))
        print(f"Received from {addr}: {parsed}")
    except json.JSONDecodeError:
        print(f"Invalid JSON from {addr}: {data}")