import time
import logging
import socket
from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.services import ReadDataByIdentifier, DiagnosticSessionControl
from udsoncan.exceptions import NegativeResponseException

logging.basicConfig(level=logging.DEBUG)  # Detailed logging

DOIP_GATEWAY_IP = "172.16.222.197"
DOIP_PORT = 13400

def main():
    # Set socket timeout
    socket.setdefaulttimeout(10.0)

    # Try different logical addresses
    logical_addresses = [0x0E00, 0x1000, 0xE000, 0x0E01]
    for addr in logical_addresses:
        print(f"\nTrying client logical address: {hex(addr)}")
        try:
            print(f"Attempting to connect to DoIP gateway {DOIP_GATEWAY_IP}:{DOIP_PORT}")
            doip = DoIPClient(DOIP_GATEWAY_IP, DOIP_PORT, client_logical_address=addr, activation_type=0)
            print("Connected to DoIP gateway")
            
            # Discover ECUs
            try:
                ecus = doip.discover()
                print("Discovered ECUs:", ecus)
            except Exception as e:
                print("ECU discovery failed:", e)
            
            # Proceed with UDS if connected
            connector = DoIPClientUDSConnector(doip)
            with Client(connector, request_timeout=5.0) as client:
                try:
                    client.change_session(DiagnosticSessionControl.Session.defaultSession)
                    print("Diagnostic session established")
                except Exception as e:
                    print("Session change failed:", e)
                    continue

                # Read VIN
                try:
                    resp = client.read_data_by_identifier(0xF190)
                    vin = resp.service_data.get(0xF190)
                    if isinstance(vin, (bytes, bytearray)):
                        vin = vin.decode('ascii', errors='ignore')
                    print("VIN:", vin)
                    return  # Exit if successful
                except NegativeResponseException as nre:
                    print("VIN read negative response:", nre)
                except Exception as e:
                    print("VIN read failed:", e)

        except ConnectionRefusedError as e:
            print(f"Connection refused by {DOIP_GATEWAY_IP}:{DOIP_PORT}: {e}")
            print("Check if the gateway is listening and if the vehicle is in diagnostic mode.")
        except TimeoutError as e:
            print(f"Connection timed out to {DOIP_GATEWAY_IP}:{DOIP_PORT}: {e}")
        except Exception as e:
            print(f"Unexpected error during DoIP connection: {e}")
    
    print("\nAll connection attempts failed. Verify IP, port, vehicle state, and logical address.")

if __name__ == "__main__":
    main()