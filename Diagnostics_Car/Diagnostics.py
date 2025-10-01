# bmw_doip_example.py
import time
import logging

from doipclient import DoIPClient
from doipclient.connectors import DoIPClientUDSConnector
from udsoncan.client import Client
from udsoncan.services import ReadDataByIdentifier, DiagnosticSessionControl
from udsoncan.exceptions import NegativeResponseException

logging.basicConfig(level=logging.INFO)

DOIP_GATEWAY_IP = "172.16.222.197"   # common gateway address for ENET BMW
DOIP_PORT = 13400

def main():
    # 1) Connect low-level DoIP
    print("Connecting to DoIP gateway", DOIP_GATEWAY_IP)
    doip = DoIPClient(DOIP_GATEWAY_IP, DOIP_PORT)
    # doip.discover()  # optional: discover ECUs on the network

    # 2) Wrap DoIP as a UDS transport for udsoncan
    connector = DoIPClientUDSConnector(doip)

    # 3) Make a UDS client on top of the DoIP connector
    with Client(connector, request_timeout=2.0) as client:
        # 4) Start a diagnostic session (default)
        try:
            client.change_session(DiagnosticSessionControl.Session.defaultSession)
        except Exception as e:
            print("Session change failed or not required:", e)

        # 5) Read VIN (common DID 0xF190 is standard)
        try:
            resp = client.read_data_by_identifier(0xF190)
            vin = resp.service_data.get(0xF190)
            if isinstance(vin, (bytes, bytearray)):
                vin = vin.decode('ascii', errors='ignore')
            print("VIN:", vin)
        except NegativeResponseException as nre:
            print("VIN read negative response:", nre)
        except Exception as e:
            print("VIN read failed:", e)

        # 6) Example: Try reading a typical vehicle speed DID (BMW-specific, may vary)
        # Replace DID_SPEED with the correct DID for your module
        DID_SPEED = 0xF40D  # example only — may not work for your car/version
        try:
            resp = client.read_data_by_identifier(DID_SPEED)
            raw = resp.service_data.get(DID_SPEED)
            print("Raw speed bytes:", raw)
            # You will need the correct scaling: many BMW DIDs are one or two bytes
        except Exception as e:
            print("Read speed failed or DID not supported:", e)

        # Keep alive for a sec
        time.sleep(1)

if __name__ == "__main__":
    main()
