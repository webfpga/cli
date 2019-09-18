import json
import requests

BACKEND_URL = "https://backend.webfpga.io/v1/api"

def Synthesize(output_bitstream, input_verilog, no_cache):
    print("Connecting to remote synthesis engine...")
    assert_connection()

    print(f"Attempting synthesis (saving to {output_bitstream.name})...")
    for f in input_verilog:
        print("  -", f.name)
    print("")

    res = request_synthesis(input_verilog, no_cache)

# Raise error if we are unable to ascertain a positive status
# from the backend server
def assert_connection():
    r = requests.get(BACKEND_URL + "/status")
    print(r.status_code, r.text, "\n")
    if r.status_code != 200 or r.json()["status"] != "ok":
        raise Exception("Backend is unreachable")

# Submit Verilog source files to the synthesis engine
def request_synthesis(input_verilog, no_cache):
    # Assemble file name and contents into JSON object for transmission
    files = []
    for f in input_verilog:
        body = f.read()
        files.append({"name": f.name, "body": body})
    print(files)

    headers = {"X-WEBFPGA-CACHE": ("false" if no_cache else "true")}
    print("request headers", headers)

    payload = json.dumps({"files": files})
    url = BACKEND_URL + "/synthesize"
    res = requests.post(url, data=payload, headers=headers)

    print(res.json())
