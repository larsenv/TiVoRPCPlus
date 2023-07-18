# TiVoRPCPlus
Discord rich presence for TiVo made in Python3.

## Installation
You can grab a ready-to-use 

## Configuration
Edit config.json as follows:

| Key | Value |
| ------ | ------ |
| tivo_ip | Your TiVo Box IP |
| tvguide_url | Zap2it Program Guide Link (see Important Notes) |

## Important Notes

To get your `tvguide_url` you will need to go on [Zap2it](https://tvschedule.zap2it.com/) website then correctly select your provider. In Developer Mode, go on Network then you can find a URL with `grid` in its name. Copy that to the config.json

You __NEED__ to enable Network Remote Control in your TiVo settings. Google how to do this for your specific TiVo box.

Thanks to dwilliamsuk for the original TiVoRPC app.