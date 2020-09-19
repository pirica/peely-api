import io
import json
import random
import textwrap
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response
from PIL import ImageFont, Image, ImageDraw

from modules.stats import updatestats


async def handler(req):
    await updatestats(req)
    lang = 'en'
    for i in req.query_args:
        if i[0] == 'lang':
            lang = str(i[1])
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
                f'https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game?lang={lang}') as req:
            if req.status != 200:
                try:
                    data = (json.loads(await (await aiofiles.open(f'Cache/content-{lang}.json', mode='r')).read()))[
                        'savetheworldnews']
                except:
                    return sanic.response.json({'status': 500, 'message': 'Intern Server error'}, status=500)
            else:
                data = (await req.json())['savetheworldnews']
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'image': "error",
            'messages': [],
        }
    }
    try:
        if data['news']['messages']:
            for motd in data['news']['messages']:
                response['data']['messages'].append({
                    'image': motd['image'],
                    'adspace': motd['adspace'],
                    'title': motd['title'],
                    'body': motd['body'],
                    'spotlight': motd['spotlight']
                })
    except KeyError as ex:
        print(ex)

    try:
        imgs = []
        for i in response["data"]["messages"]:
            img = Image.new("RGBA", (1024, 512))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(i['image']) as temp:
                    img.paste(Image.open(io.BytesIO(await temp.read())))
            draw = ImageDraw.Draw(img)
            draw.text((img.width - img.width + 25, 365), f"{i['title']}", (255, 255, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45))
            draw.text((img.width - img.width + 25, 415), f"{textwrap.fill(i['body'], 70)}", (51, 237, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 20))
            imgs.append(img)

        img.save(fp=f"cdn/unique/stwnews_{lang}.gif", format='GIF', append_images=imgs, save_all=True, duration=4500,
                 loop=0)
        response['data']['image'] = f"https://api.peely.de/cdn/unique/stwnews_{lang}.gif"
    except:
        traceback.print_exc()

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
