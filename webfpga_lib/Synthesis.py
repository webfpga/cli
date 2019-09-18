import json
import pprint
import requests
import asyncio
import websockets
from colorama import init
from termcolor import colored

# Cross-platform Colorama support
init()
print(colored('Colorama support', 'red'))

BACKEND_URL = "https://backend.webfpga.io/v1/api"
WSS_URL     = "wss://backend.webfpga.io/v1/ws"

async def Synthesize(output_bitstream, input_verilog, no_cache):
    # Ensure that the backend is online
    print("Connecting to remote synthesis engine...")
    assert_connection()

    # Submit synthesis job to the backend
    print(f"Attempting synthesis (saving to {output_bitstream.name})...")
    for f in input_verilog:
        print("  -", f.name)
    res = request_synthesis(input_verilog, no_cache)

    # Follow synthesis log
    id = res["id"]
    print(f"\nSubscribing to synthesis log (id={id})...")
    async with websockets.connect(WSS_URL) as ws:
        payload = {"type": "subscribe", "id": id}
        await ws.send(json.dumps(payload))

        while True:
            msg = await ws.recv()
            print_ws_msg(msg)

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
    #print(files)

    headers = {"X-WEBFPGA-CACHE": ("false" if no_cache else "true")}
    #print("request headers", headers)

    payload = json.dumps({"files": files})
    url = BACKEND_URL + "/synthesize"
    res = requests.post(url, data=payload, headers=headers)
    pprint.pprint(res.json())

    return res.json()

# Print a websocket synthesis-log message
def print_ws_msg(raw_msg):
    data = json.loads(raw_msg)
    if (data["type"] != "synthesis-log"):
        return

    for msg in data["msg"]:
        if msg.startswith("#*"):
            fields = msg.split(" ")
            color  = fields[0][2:]
            print(colored(" ".join(fields[1:]), color))
        else:
            print(msg)
