import json


import aiofiles
import aiohttp
import sanic
import sanic.response

import io
import random
import textwrap
import traceback
from PIL import ImageFont, Image, ImageDraw


async def handler(req):
    lang = 'en'
    for i in req.query_args:
        if i[0] == 'lang':
            lang = str(i[1])
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
                f'https://fortnitecontent-website-prod07.ol.epicgames.com/content/api/pages/fortnite-game?lang={lang}') as req:
            if req.status != 200:
                try:
                    data = (json.loads(await (await aiofiles.open(f'Cache/content-{lang}.json', mode='r')).read()))
                except:
                    return sanic.response.json({'status': 500, 'message': 'Intern Server error'})
            else:
                data = (await req.json())
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'image': "error",
            'motds': [],
            'messages': [],
            'platform_motds': {},
            'ads': []
        }
    }
    try:
        if data['creativenews']['news']['motds']:
            for motd in data['creativenews']['news']['motds']:
                response['data']['motds'].append({
                    'image': motd['image'],
                    'tileImage': motd['tileImage'],
                    'title': motd['title'],
                    'body': motd['body'],
                    'id': motd['id'],
                    'spotlight': motd['spotlight']
                })
    except:
        traceback.print_exc()
    try:
        if data['creativenews']['news']['messages']:
            for message in data['creativenews']['news']['messages']:
                response['data']['messages'].append({
                    'image': message['image'],
                    'messagetype': message['messagetype'],
                    'title': message['title'],
                    'body': message['body'],
                    'spotlight': message['spotlight']
                })
    except:
        traceback.print_exc()

    try:
        if data['creativenews']['news']['platform_motds']:
            for platform in data['creativenews']['news']['platform_motds']:
                response['data']['platform_motds'][platform['platform']] = []
            for platform_motds in data['creativenews']['news']['platform_motds']:
                response['data']['platform_motds'][platform_motds['platform']].append({
                    'image': platform_motds['message']['image'],
                    'tileImage': platform_motds['message']['tileImage'],
                    'title': platform_motds['message']['title'],
                    'body': platform_motds['message']['body'],
                    'id': platform_motds['message']['id'],
                    'spotlight': platform_motds['message']['spotlight']
                })
    except:
        traceback.print_exc()

    try:
        if data['creativeAds']['ad_info']['ads']:
            for ad in data['creativeAds']['ad_info']['ads']:
                try:
                    response['data']['ads'].append({
                        'title': ad['header'],
                        'description': ad['description'],
                        'image': ad['image'],
                        'hidden': ad['hidden'],
                    })
                except:
                    continue
    except:
        traceback.print_exc()

    try:
        imgs=[]
        for i in response["data"]["motds"]:
            img = Image.new("RGBA", (1024, 512))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(i['tileImage']) as temp:
                    img.paste(Image.open(io.BytesIO(await temp.read())))
            draw = ImageDraw.Draw(img)
            draw.text((img.width - img.width + 25, 365), f"{i['title']}", (255, 255, 255), font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45))
            draw.text((img.width - img.width + 25, 415), f"{textwrap.fill(i['body'], 70)}", (51, 237, 255), font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 20))
            imgs.append(img)

        id = random.randint(1111111111111, 99999999999999999999)
        img.save(fp=f"cdn/unique/creative_news_{id}.gif", format='GIF', append_images=imgs, save_all=True, duration=3200, loop=0)
        response['data']['image'] = f"https://api.peely.de/cdn/unique/creative_news_{id}.gif"
    except:
        traceback.print_exc()

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
