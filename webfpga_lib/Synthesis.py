import requests

BACKEND_URL = "https://backend.webfpga.io/v1/api"

def Synthesize(output_bitstream, input_verilog):
    print("Connecting to remote synthesis engine...")
    assert_connection()

    print(f"Attempting synthesis (saving to {output_bitstream.name})...")
    for f in input_verilog:
        print("  -", f.name)

# Raise error if we are unable to ascertain a positive status
# from the backend server
def assert_connection():
    r = requests.get(BACKEND_URL + "/status")
    print(r.status_code, r.text, "\n")
    if r.status_code != 200 or r.json()["status"] != "ok":
        raise Exception("Backend is unreachable")
