import time
import socket
import json
import sys
import requests
import callsigns
from pypresence import Presence

## Load Config File
with open("config.json", "r") as config:
    configjson = json.load(config)
    print("Config Loaded")

## TiVo TCP Config
TCP_IP = configjson["tivo_ip"]
TCP_PORT = 31339
BUFFER_SIZE = 30

## RPC Config
CLIENT_ID = "993635110333198449"
RPC = Presence(CLIENT_ID)
RPC.connect()

PCN = ""

tivo_images = {
    "110": "series2",
    "130": "series2",
    "140": "series2",
    "230": "series2",
    "264": "series2",
    "275": "series2",
    "540": "series2",
    "565": "series2",
    "590": "series2",
    "595": "series2",
    "648": "series3oled",
    "649": "series2",
    "652": "series3xl",
    "658": "series3xl",
    "746": "premiere",
    "748": "premiere",
    "750": "premiere",
    "758": "premiere",
    "840": "roamiopro",
    "846": "roamio",
    "848": "roamiopro",
    "849": "bolt",
    "A92": "mini",
    "A95": "minivox",
    "D6E": "edge",
    "D6F": "edge",
}

tivo_names = {
    "110": "TiVo Series 2 Sony SVR-3000",
    "130": "TiVo Series 2 AT&T 130",
    "140": "TiVo Series 2 140",
    "230": "TiVo Series 2 AT&T 230",
    "264": "TiVo Series 2 Toshiba",
    "275": "TiVo Series 2 Pioneer DVD Burner",
    "540": "TiVo Series 2 540",
    "565": "TiVo Series 2 Toshiba DVD Burner",
    "590": "TiVo Series 2 Humax",
    "595": "TiVo Series 2 Humax DVD Burner",
    "648": "TiVo Series 3 OLED",
    "649": "TiVo Series 2 Dual Tuner",
    "652": "TiVo Series 3 HD",
    "658": "TiVo Series 3 XL",
    "746": "TiVo Premiere",
    "748": "TiVo Premiere XL",
    "750": "TiVo Premiere 4",
    "758": "TiVo Premiere XL4",
    "840": "TiVo Roamio Pro",
    "846": "TiVo Roamio",
    "848": "TiVo Roamio Plus",
    "849": "TiVo Bolt",
    "A92": "TiVo Mini",
    "A95": "TiVo Mini VOX",
    "D6E": "TiVo Edge Cable",
    "D6F": "TiVo Edge Antenna",
}


## Get TiVo Image
def get_tivo_model():
    try:
        response = requests.head("http://" + configjson["tivo_ip"] + "/")
        return response.headers.get("Server").split(":")[2]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


## Get TiVo Image
def get_tivo_image(model):
    image = tivo_images[model]
    return image


## Get TiVo Name
def get_tivo_name(model):
    image = tivo_names[model]
    return image


## Get Current Channel
def get_chan():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((TCP_IP, TCP_PORT))
    except ConnectionRefusedError:
        print(
            "Connection Refused. This probably means your TiVo doesn't have network remote control enabled."
        )
        sys.exit(1)
    data = s.recv(BUFFER_SIZE)
    s.close()
    ccn = "".join(filter(str.isdigit, str(data)))
    try:
        if len(ccn) == 8:
            ccn2 = str(int(ccn[-4:]))
            ccn = str(int(ccn[:-4]))
            ccn += "-" + ccn2
        else:
            ccn = str(int(ccn))
    except ValueError:
        print(
            "Couldn't find the channel you're on. Try going into TiVo Central and exit it."
        )
        sys.exit(1)
    if b"RECORDING" in data:
        ccn += " 🔴"
    return ccn


## Get Guide Data from Zap2it
def get_guide_data():
    try:
        return requests.get(
            configjson["tvguide_url"].split("time=")[0]
            + "time="
            + str(int(time.time()))
            + "&pref="
            + configjson["tvguide_url"].split("&pref=")[1]
        ).json()["channels"]
    except requests.exceptions.JSONDecodeError:
        return


## Get Channel Name From Number
def get_name(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                if channel["callSign"] in callsigns.callsigns:
                    return callsigns.callsigns[channel["callSign"]]
                else:
                    return channel["callSign"]

    return False


## Get Full Channel Name From Number
def get_full_name(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                if channel["callSign"] not in callsigns.callsigns:
                    if channel["affiliateName"] != "":
                        return " - " + channel["affiliateName"]
                    else:
                        return ""
                else:
                    return ""

    return False


## Get Show Name from Number
def get_show_name(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                return channel["events"][0]["program"]["title"]

    return False


## Get Show Name from Number
def get_episode_title(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                return channel["events"][0]["program"]["episodeTitle"]

    return False


global i

i = 1

current_time = time.time()

IDLE_TIME = int(configjson["idle_time"])  # Change in order to timeout after more time
IDLE_LAST = 0
IDLE_CHANNEL = ""


## RPC Updater
def update_rpc():
    global PCN, IDLE_CHANNEL, IDLE_LAST
    ccn = get_chan()
    IDLE_CHANNEL = ccn
    activity = ""
    guide_data = get_guide_data()
    name = get_name(guide_data, ccn)
    if name is False:
        name = ""
    full_name = get_full_name(guide_data, ccn)
    if full_name is False:
        full_name = ""
    model = get_tivo_model()
    image = get_tivo_image(model)
    tivo_name = get_tivo_name(model)
    show_name = get_show_name(guide_data, ccn)
    episode_title = get_episode_title(guide_data, ccn)
    if show_name is not False:
        activity += show_name
    if episode_title:
        if len(activity + episode_title) <= 62:
            activity += " - " + episode_title
    name += " - Channel " + ccn
    if name != full_name and name is not None:
        name += full_name
    if "🔴" in name:
        name = name.replace(" 🔴", "")
        activity += " - " + "🔴 REC"
    if activity == PCN or i % 6 == 0:
        if time.time() - IDLE_TIME > IDLE_LAST:
            RPC.clear()
            return "Idling."
        return "No need to update, sleeping for 5 seconds"
    elif ccn.split("-", maxsplit=1)[0].isnumeric() is False:
        return "Error while grabbing current channel, ensure that TiVo IP is correct or that multiple instances aren't running"
    else:
        PCN = activity
        IDLE_LAST = time.time()
        IDLE_CHANNEL = ccn

        if name is False:
            current_time = time.time()

            return RPC.update(
                pid=1416189551,
                state=activity,
                large_image=image,
                large_text=tivo_name,
                small_image="tivologo",
                small_text="TiVo Logo",
                start=current_time,
            )
        else:
            current_time = time.time()

            return RPC.update(
                pid=1416189551,
                state=activity,
                details=name,
                large_image=image,
                large_text=tivo_name,
                small_image="tivologo",
                small_text="TiVo Logo",
                start=current_time,
            )


## The Magic Stuffs
while True:
    try:
        print(update_rpc())
        time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
        RPC.close()
        sys.exit()
    except Exception as e:
        print("Error: " + str(e))
        time.sleep(5)
