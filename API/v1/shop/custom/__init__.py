import io
import json
import random

import aiofiles
import aiohttp
import sanic
import sanic.response

from modules import customshop


async def handler(req):
    background = "https://peely.de/api/background.jpg"
    text = "Fortnite Item Shop"
    lang = "en"
    featured = "Featured"
    daily = "Daily"
    for i in req.query_args:
        if i[0].lower() == "background":
            background = i[1]
        if i[0].lower() == "text":
            text = i[1]
        if i[0].lower() == "lang":
            lang = i[1].lower()
        if i[0].lower() == "featured":
            featured = i[1].lower()
        if i[0].lower() == "daily":
            daily = i[1].lower()

    if lang != "en":
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://fortnite-api.com/v1/shop/br?language={lang}") as resp:
                if resp.status != 200:
                    data = data = dict(json.loads(
                        await (await aiofiles.open('Cache/data/shop.json', mode='r')).read()))["data"]
                else:
                    data = (await resp.json())["data"]
    else:
        data = dict(json.loads(
            await (await aiofiles.open('Cache/data/shop.json', mode='r')).read()))["data"]
    img = await customshop.GenerateShopImage(Store=data,
                                             background_user=background, text=text, featured=featured, daily=daily)
    rand = random.randint(1111111111111111111111111111111111111111, 99999999999999999999999999999999999999999999999999)
    img.save(f"cdn/unique/{rand}.png")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return await sanic.response.file(f"cdn/unique/{rand}.png")
