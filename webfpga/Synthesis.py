import json
import base64
import pprint
import requests
import asyncio
import websockets
import colorama
import termcolor
from termcolor import colored

# Cross-platform Colorama support
colorama.init()

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
    id = res["id"]
    print("")

    # Check if the cached result already exists
    if res["cached"]:
        print("Cached bitstream already exists!")
        bitstream = download_bitstream(id)
        if bitstream["ready"]:
            save_bitstream(bitstream, output_bitstream)
            return

    # Follow synthesis log
    print(f"\nSubscribing to synthesis log (id={id})...")
    async with websockets.connect(WSS_URL) as ws:
        payload = {"type": "subscribe", "id": id}
        await ws.send(json.dumps(payload))

        while True:
            # Block websocket until we receive a message
            raw_msg = await ws.recv()
            data = json.loads(raw_msg)

            # Confirm subscription registration
            if (data["type"] == "subscribe"):
                if data["success"]:
                    print("Subscription success!\n")
                else:
                    raise Exception("Failed to subscribe to synthesis log stream")

            # not a message, just print the json response
            if not "msg" in data:
                print(data)
                continue

            # print the message and break when synthesis is complete
            print_ws_msg(data)
            for msg in data["msg"]:
                if "synthesis complete" in msg:
                    print("Synthesis complete! Downloading bitstream...")
                    bitstream = download_bitstream(id)
                    save_bitstream(bitstream, output_bitstream)
                    return

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
def print_ws_msg(data):
    for msg in data["msg"]:
        if msg.startswith("#*"):
            fields = msg.split(" ")
            color  = fields[0][2:]
            # Colorama+Termcolors doens't support 256 colors
            # We could use a different library (e.g. Colored), but
            # then we would lose Windows support
            if not color in termcolor.COLORS:
                color = "yellow"
            print(colored(" ".join(fields[1:]), color))
        else:
            print(msg)

def download_bitstream(id):
    res = requests.get(BACKEND_URL + "/bitstream/" + id).json()
    print(res)
    return res

def save_bitstream(bitstream, output_file):
    print("Saving bitstream...")
    b = base64.b64decode(bitstream["bitstream"])
    output_file.write(b)
