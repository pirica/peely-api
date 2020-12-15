import io
import json
import math
import random
import time
import traceback
from datetime import datetime

import aiofiles
import discord
import sanic
import sanic.response
from PIL import Image
from discord.ext import commands

from modules import leaks


async def handler(req):
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/data/resp_leaks.json', mode='r')).read()))


async def generateleaks(data: dict, client: commands.Bot):
    await (await aiofiles.open('Cache/data/leaks.json', mode='w+')).write(
        json.dumps(data, indent=2))
    start = time.time() + random.randint(1111, 9999)
    files = [await leaks.GenerateCard(i) for i in data["data"]["items"]]
    if not files:
        raise FileNotFoundError("No Images")
    await client.get_channel(735018804169670687).send(f"New Leaks detected")
    result = Image.new("RGBA", (
        round(math.sqrt(len(files)) + 0.45) * 305 - 5, round(math.sqrt(len(files))) * 550 - 5))
    result.paste(Image.open("assets/Images/Backgrounds/Background.png").resize(
        (
            int(round(math.sqrt(len(files)) + 0.45) * 305 - 5),
            int(round(math.sqrt(len(files)) + 0.45) * 550 - 5)),
        Image.ANTIALIAS))
    x = -305
    y = 0
    count = 0
    for img in files:
        try:
            img.thumbnail((305, 550), Image.ANTIALIAS)
            w, h = img.size
            if count >= round(math.sqrt(len(files)) + 0.45):
                y += 550
                x = -305
                count = 0
            x += 305
            count += 1
            result.paste(img, (x, y, x + w, y + h))
        except:
            continue
    result.save("cdn/current/leaks.png", optimized=True)
    uniqueimage = str(datetime.utcnow().__format__('%A, %B %d, %Y'))
    result.save(f"cdn/unique/leaks_{uniqueimage}.png", optimize=True)
    buffered = io.BytesIO()
    result.save(buffered, format="PNG")
    buffered.seek(0)
    data = {
        "url": "https://api.peely.de/cdn/current/leaks.png",
        "uniqueurl": f"https://api.peely.de/cdn/unique/leaks_{uniqueimage}.png",
        "time": str(datetime.utcnow().__format__('%A, %B %d, %Y'))
    }

    await (await aiofiles.open('Cache/data/resp_leaks.json', mode='w+')).write(
        json.dumps(data, indent=2))
    await client.get_channel(735018804169670687).send(
        f"Updated Leaks. Generating Image in {round(time.time() - start, 2)}sec")
