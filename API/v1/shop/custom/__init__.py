import io
import json
import random

import aiofiles
import sanic
import sanic.response

from modules import customshop


async def handler(req):
    background = "http://peely.de/api/background.jpg"
    text = "Fortnite Item Shop"
    for i in req.query_args:
        if i[0] == "background":
            background = i[1]
        if i[0] == "text":
            text = i[1]
    img = await customshop.GenerateShopImage(Store=dict(json.loads(
        await (await aiofiles.open('Cache/data/shop.json', mode='r')).read()))["data"],
                                             background_user=background, text=text)
    rand = random.randint(1111111111111111111111111111111111111111, 999999999999999999999999999999999999999999999999)
    print(rand)
    img.save(f"cdn/temp/{rand}.png")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return await sanic.response.file(f"cdn/temp/{rand}.png")
