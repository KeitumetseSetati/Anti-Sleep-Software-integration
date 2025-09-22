import socket
import struct
import json
import csv
import os
from datetime import datetime

MCAST_GRP = "239.0.0.57"
MCAST_PORT = 12345

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', MCAST_PORT))  # Listen on all interfaces

# Join multicast group
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

print(f"Listening on multicast {MCAST_GRP}:{MCAST_PORT}")

# ----------------------
# Setup CSV file
# ----------------------
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"sensor_log_{timestamp}.csv"

fieldnames = ["time", "accel_x", "accel_y", "accel_z", 
              "gyro_x", "gyro_y", "gyro_z", "temp_c"]

file_exists = os.path.isfile(csv_filename)

with open(csv_filename, mode="a", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header if file is new
    if not file_exists:
        writer.writeheader()

    # ----------------------
    # Main loop
    # ----------------------
    while True:
        data, addr = sock.recvfrom(1024)
        try:
            parsed = json.loads(data.decode('utf-8'))

            row = {
                "time": datetime.now().isoformat(),
                "accel_x": parsed.get("accel_x"),
                "accel_y": parsed.get("accel_y"),
                "accel_z": parsed.get("accel_z"),
                "gyro_x": parsed.get("gyro_x"),
                "gyro_y": parsed.get("gyro_y"),
                "gyro_z": parsed.get("gyro_z"),
                "temp_c": parsed.get("temp_c")
            }

            writer.writerow(row)
            csvfile.flush()  # ensure data is written immediately

            print(f"Saved row from {addr}: {row}")

        except json.JSONDecodeError:
            print(f"Invalid JSON from {addr}: {data}")