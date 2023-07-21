from pypresence import Presence
import callsigns
import time
import socket
import json
import requests
import sys

## Load Config File
with open("config.json") as config:
    configjson = json.load(config)
    print("Config Loaded")

## TiVo TCP Config
TCP_IP = configjson["tivo_ip"]
TCP_PORT = 31339
BUFFER_SIZE = 30

## RPC Config
client_id = "993635110333198449"
RPC = Presence(client_id)
RPC.connect()

pcn = ""

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
def getTiVoModel():
    try:
        response = requests.head("http://" + configjson["tivo_ip"] + "/")
        return response.headers.get("Server").split(":")[2]
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


## Get TiVo Image
def getTiVoImage(model):
    image = tivo_images[model]
    return image


## Get TiVo Name
def getTiVoName(model):
    image = tivo_names[model]
    return image


## Get Current Channel
def getChan():
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
def getGuideData():
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
def getName(guide_data, num):
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
def getFullName(guide_data, num):
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
def getShowName(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                return channel["events"][0]["program"]["title"]

    return False


## Get Show Name from Number
def getEpisodeTitle(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num:
                return channel["events"][0]["program"]["episodeTitle"]

    return False


global i

i = 1

current_time = time.time()

idle_time = 1800  # Change in order to timeout after more time
idle_last = 0
idle_channel = ""

## RPC Updater
def updateRPC():
    global pcn, idle_channel, idle_time, idle_last
    ccn = getChan()
    idle_channel = ccn
    activity = ""
    guide_data = getGuideData()
    name = getName(guide_data, ccn)
    if name is False:
        name = ""
    full_name = getFullName(guide_data, ccn)
    if full_name is False:
        full_name = ""
    model = getTiVoModel()
    image = getTiVoImage(model)
    tivo_name = getTiVoName(model)
    show_name = getShowName(guide_data, ccn)
    episode_title = getEpisodeTitle(guide_data, ccn)
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
    if activity == pcn or i % 6 == 0:
        if time.time() - idle_time > idle_last:
            RPC.clear()
            return "Idling."
        return "No need to update, sleeping for 5 seconds"
    elif ccn.split("-")[0].split(" ")[0].isnumeric() == False:
        return "Error while grabbing current channel, ensure that TiVo IP is correct or that multiple instances aren't running"
    else:
        pcn = activity
        idle_last = time.time()
        idle_channel = ccn

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
        print(updateRPC())
        time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting...")
        RPC.close()
        sys.exit()
