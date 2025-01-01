# TiVoRPCPlus
Discord rich presence for TiVo made in Python 3.

<img src="http://transfer.archivete.am/12SfPn/%60.png" alt="Preview" width="500"/>

## Features
- Shows what program you're watching, the channel number, network, and if you're recording or not.
- Setting to hide your rich presence if you don't change channels after a given time.
- Rich presence changes automatically when you change channels.
- Picture of your TiVo DVR's shown correlating with the TiVo model you own.
- Works on Series 2, Series 3, Premiere, Roamio, BOLT, Edge, Mini, and Virgin Media TiVos.

## Installation
You can grab a compiled version of the program [here](https://github.com/larsenv/TiVoRPCPlus/releases/latest). You will need to rename config.json.example to config.json then edit it which is covered on the next section. It needs to be in the same folder as the program.

## Configuration
Edit config.json as follows.

| Key | Value |
| ------ | ------ |
| idle_time | How many seconds to time out rich presence if the channel wasn't changed or a recording wasn't started. |
| tivo_ip | Your TiVo Box IP. |
| tvguide_url | Zap2it Program Guide Link (see Important Notes). |

## Important Notes
To get your `tvguide_url` you will need to go on [Zap2it](https://tvschedule.zap2it.com/) website then correctly select your provider. In Developer Mode, go on Network then you can find a URL with `grid` in its name. Copy that to the config.json.

You must turn Network Remote Control on your TiVo in order to use rich presence.

Thanks to dwilliamsuk for the original TiVoRPC app.
