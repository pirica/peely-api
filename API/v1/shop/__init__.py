import io
import json
import time
import traceback
from datetime import datetime

import aiofiles
import discord
import sanic
import sanic.response
from PIL import Image
from discord.ext import commands

from modules import shop


async def handler(req):
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/data/resp_shop.json', mode='r')).read()))


async def generaterequest(Store: dict, client: commands.Bot):
    await client.get_channel(735018804169670687).send(f"New Shop detected")
    start = time.time()
    await (await aiofiles.open('Cache/data/shop.json', mode='w+')).write(
        json.dumps(Store, indent=2))
    newimage = await shop.GenerateShopImage(client, Store["data"])
    newimage.save("cdn/current/shop.png", optimize=True)
    uniqueimage = time.time()
    newimage.save(f"cdn/unique/shop_{uniqueimage}.png", optimize=True)
    buffered = io.BytesIO()
    newimage.save(buffered, format="PNG")
    buffered.seek(0)
    data = {
        "url": "https://api.peely.de/cdn/current/shop.png",
        "uniqueurl": f"https://api.peely.de/cdn/unique/shop_{uniqueimage}.png",
        "time": str(datetime.utcnow().__format__('%A, %B %d, %Y'))
    }
    try:
        file = discord.File(f"cdn/current/shop.png")
        msg = await client.get_channel(id=707854587297792051).send("New shop generated", file=file)
        if msg.attachments[0]:
            discordsize = True
            data['discordurl'] = str(msg.attachments[0].url)
        else:
            discordsize = False
            data["discordurl"] = "Failed to upload the Image to Discord. (?CDN Server down?)"
    except Exception as ex:
        traceback.print_exc()
        discordsize = False
        data["discordurl"] = "Failed to upload the Image to Discord. (?CDN Server down?)"
    if discordsize is False:
        for tint in range(2, 11):
            temp = Image.open("cdn/current/shop.png")
            x = int(round(temp.size[0] / tint))
            y = int(round(temp.size[1] / tint))
            print(x, y)
            temp = temp.resize((x, y), Image.ANTIALIAS)
            temp.save("cdn/current/shop.png", optimize=True, quality=int(round(100 / tint)))
            temp.save(io.BytesIO(), format="PNG")
            try:
                try:
                    file = discord.File(f"cdn/current/shop.png")
                    msg = await client.get_channel(id=707854587297792051).send("New shop generated", file=file)
                    if msg.attachments[0]:
                        break
                except:
                    continue
            except discord.HTTPException:
                continue

    await (await aiofiles.open('Cache/data/resp_shop.json', mode='w+')).write(
        json.dumps(data, indent=2))
    await client.get_channel(735018804169670687).send(
        f"Updated Shop. Generating Image in {round(time.time() - start, 2)}sec")
