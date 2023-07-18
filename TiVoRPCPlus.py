from pypresence import Presence
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
client_id = configjson["client_id"]
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
    "D6E": "edge",
    "D6F": "edge",
}

## Get TiVo Image
def getTiVoImage():
    try:
        response = requests.head("http://" + configjson["tivo_ip"] + "/")
        image = tivo_images[response.headers.get("Server").split(":")[2]]
        return image
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


## Get Current Channel
def getChan():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    data = s.recv(BUFFER_SIZE)
    s.close()
    ccn = "".join(filter(str.isdigit, str(data)))
    if len(ccn) == 8:
        ccn2 = str(int(ccn[-4:]))
        ccn = str(int(ccn[:-4]))
        ccn += "-" + ccn2
    else:
        ccn = str(int(ccn))
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
            if channel["channelNo"] == num.replace("-", "."):
                return channel["callSign"]

    return False


## Get Full Channel Name From Number
def getFullName(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num.replace("-", "."):
                return channel["affiliateName"]

    return False


## Get Show Name from Number
def getShowName(guide_data, num):
    num = str(num.replace("-", ".").split(" ")[0])

    if guide_data:
        for channel in guide_data:
            if channel["channelNo"] == num.replace("-", "."):
                return channel["events"][0]["program"]["title"]

    return False


global i

i = 1

## RPC Updater
def updateRPC():
    global pcn
    ccn = getChan()
    guide_data = getGuideData()
    name = getName(guide_data, ccn)
    full_name = getFullName(guide_data, ccn)
    image = getTiVoImage()
    if name != full_name and name is not None:
        name += " - " + full_name
    if name is None:
        name = full_name
    show_name = getShowName(guide_data, ccn)
    if show_name is not False:
        ccn += " - " + show_name
    if "🔴" in ccn:
        ccn = ccn.replace(" 🔴", "") + " 🔴"
    if ccn == pcn or i % 6 == 0:
        return "No need to update, sleeping for 5 seconds"
    elif ccn.split("-")[0].split(" ")[0].isnumeric() == False:
        return "Error while grabbing current channel, ensure that TiVo IP is correct or that multiple instances aren't running"
    else:
        pcn = ccn
        if name == False:
            return RPC.update(
                state="Channel " + ccn,
                large_image=image,
                large_text="Channel " + ccn,
            )
        else:
            return RPC.update(
                state="Channel " + ccn,
                details=name,
                large_image=image,
                large_text="Channel " + ccn,
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
