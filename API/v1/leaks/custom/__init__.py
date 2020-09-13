import io
import json
import random

import aiofiles
import aiohttp
import sanic
import sanic.response

from modules import customleaks
from modules.stats import updatestats


async def handler(req):
    await updatestats(req)
    background = "https://peely.de/api/background.jpg"
    text = "Fortnite Leaks"
    lang = "en"
    for i in req.query_args:
        if i[0].lower() == "background":
            background = i[1]
        if i[0].lower() == "text":
            text = i[1]
        if i[0].lower() == "lang":
            lang = i[1].lower()

    if lang != "en":
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://fortnite-api.com/v2/cosmetics/br/new?language={lang}") as resp:
                if resp.status != 200:
                    data = data = dict(json.loads(
                        await (await aiofiles.open('Cache/data/leaks.json', mode='r')).read()))
                else:
                    data = (await resp.json())
    else:
        data = dict(json.loads(
            await (await aiofiles.open('Cache/data/leaks.json', mode='r')).read()))
    rand = random.randint(0000000000000, 99999999999999999)
    img = await customleaks.generate(background=background, text=text, Leaks=data)
    img.save(f"cdn/unique/leaks_{lang}_{rand}.png")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return await sanic.response.file(f"cdn/unique/leaks_{lang}_{rand}.png")
