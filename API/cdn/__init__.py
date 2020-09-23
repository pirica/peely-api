import io
import json
import math
import os
import random
import time

import aiofiles
import aiohttp
import sanic
import sanic.response
from PIL import Image

from modules import shop, leaks


async def handler(req, folder, name):
    lang = "en"
    for i in req.query_args:
        if i[0] == "lang":
            lang = str(i[1]).lower()

    if lang != "en":
        if str(name).lower().startswith("shop"):
            currentshop = str((json.loads(await (await aiofiles.open(f'Cache/data/resp_shop.json', mode='r')).read()))[
                                  'uniqueurl']).split("shop_")[1].split(".png")[0]
            if os.path.exists(f"cdn/unique/shop_{lang}_{currentshop}.png") is True:
                return await sanic.response.file(f"cdn/unique/shop_{lang}_{currentshop}.png")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://fortnite-api.com/v1/shop/br?language={lang}") as resp:
                    if resp.status != 200:
                        return sanic.response.empty(status=404)
                    img = await shop.GenerateShopImage((await resp.json())['data'])
                    img.save(f"cdn/unique/shop_{lang}_{currentshop}.png", optimize=True)
                    buffered = io.BytesIO()
                    img.save(buffered, format="PNG")
                    buffered.seek(0)
                    return await sanic.response.file(f"cdn/unique/shop_{lang}_{currentshop}.png")

        if str(name).lower().startswith("leaks"):
            currentleaks = str(
                (json.loads(await (await aiofiles.open(f'Cache/data/resp_leaks.json', mode='r')).read()))[
                    'uniqueurl']).split("leaks_")[1].split(".png")[0]
            if os.path.exists(f"cdn/unique/leaks_{lang}_{currentleaks}.png") is True:
                return await sanic.response.file(f"cdn/unique/leaks_{lang}_{currentleaks}.png")
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://fortnite-api.com/v2/cosmetics/br/new?language={lang}") as resp:
                    if resp.status != 200:
                        return sanic.response.empty(status=404)
                    files = [await leaks.GenerateCard(i) for i in (await resp.json())["data"]["items"]]
                    if not files:
                        return sanic.response.empty(status=404)
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
                    imagetime = time.time() + random.randint(1111, 9999)
                    result.save(f"cdn/unique/leaks_{lang}_{currentleaks}.png", optimize=True)
                    buffered = io.BytesIO()
                    result.save(buffered, format="PNG")
                    buffered.seek(0)
                    return await sanic.response.file(f"cdn/unique/leaks_{lang}_{currentleaks}.png")

    try:
        return await sanic.response.file(f"cdn/{str(folder).lower()}/{str(name).lower()}")
    except:
        return sanic.response.empty(status=404)
