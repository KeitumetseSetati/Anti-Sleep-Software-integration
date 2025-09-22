import socket
import struct
import json

MCAST_GRP = "239.0.0.57"
MCAST_PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))  # Listen on all interfaces

# Join multicast group
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening on multicast {MCAST_GRP}:{MCAST_PORT}")

while True:
    data, addr = sock.recvfrom(1024)
    try:
        parsed = json.loads(data.decode('utf-8'))
        print(f"Received from {addr}: {parsed}")
    except json.JSONDecodeError:
        print(f"Invalid JSON from {addr}: {data}")
