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
                    data = json.loads(await (await aiofiles.open(f'Cache/content-{lang}.json', mode='r')).read())
                except:
                    return sanic.response.json({'status': 500, 'message': 'Intern Server error'}, status=500)
            else:
                data = await req.json()
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'br': {
                'image': "error",
                'motds': [],
                'messages': [],
            },
            'creative': {
                'image': "error",
                'motds': [],
                'messages': [],
                'ads': [],
            },
            'stw': {
                'image': "error",
                'messages': [],
            }
        }
    }
    try:
        if data['battleroyalenewsv2']['news']['motds']:
            for motd in data['battleroyalenewsv2']['news']['motds']:
                response['data']['br']['motds'].append({
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
        if data['battleroyalenewsv2']['news']['messages']:
            for message in data['battleroyalenewsv2']['news']['messages']:
                response['data']['br']['messages'].append({
                    'image': message['image'],
                    'messagetype': message['messagetype'],
                    'title': message['title'],
                    'body': message['body'],
                    'spotlight': message['spotlight']
                })
    except KeyError as ex:
        print(ex)

    try:
        imgs = []
        for i2 in response["data"]["br"]["motds"]:
            img = Image.new("RGBA", (1920, 1080))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(i2['image']) as temp:
                    img.paste(Image.open(io.BytesIO(await temp.read())))
            draw = ImageDraw.Draw(img)
            draw.text((img.width - img.width + 25, 835), f"{i2['title']}", (255, 255, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 60))
            draw.text((img.width - img.width + 25, 900), f"{textwrap.fill(i2['body'], 70)}", (51, 237, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45))
            imgs.append(img)

        img.save(fp=f"cdn/current/brnews_{lang}.gif", format='GIF', append_images=imgs, save_all=True,
                 duration=4500,
                 loop=0)
        response['data']['br']['image'] = f"https://api.peely.de/cdn/current/brnews_{lang}.gif"
    except:
        traceback.print_exc()

    try:
        if data['creativenewsv2']['news']['motds']:
            for motd in data['creativenewsv2']['news']['motds']:
                response['data']['creative']['motds'].append({
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
        if data['creativenewsv2']['news']['messages']:
            for message in data['creativenewsv2']['news']['messages']:
                response['data']['creative']['messages'].append({
                    'image': message['image'],
                    'messagetype': message['messagetype'],
                    'title': message['title'],
                    'body': message['body'],
                    'spotlight': message['spotlight']
                })
    except:
        traceback.print_exc()

    try:
        if data['creativeAds']['ad_info']['ads']:
            for ad in data['creativeAds']['ad_info']['ads']:
                try:
                    response['data']['creative']['ads'].append({
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
        imgs = []
        for i in response["data"]["creative"]["motds"]:
            img = Image.new("RGBA", (1920, 1080))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(i['image']) as temp:
                    img.paste(Image.open(io.BytesIO(await temp.read())))
            draw = ImageDraw.Draw(img)
            draw.text((img.width - img.width + 25, 835), f"{i['title']}", (255, 255, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 60))
            draw.text((img.width - img.width + 25, 900), f"{textwrap.fill(i['body'], 70)}", (51, 237, 255),
                      font=ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45))
            imgs.append(img)

        img.save(fp=f"cdn/current/creativenews_{lang}.gif", format='GIF', append_images=imgs, save_all=True,
                 duration=4500, loop=0)
        response['data']['creative']['image'] = f"https://api.peely.de/cdn/current/creativenews_{lang}.gif"
    except:
        traceback.print_exc()

    try:
        if data['savetheworldnews']['news']['messages']:
            for motd in data['savetheworldnews']['news']['messages']:
                response['data']['stw']['messages'].append({
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
        for i in response["data"]["stw"]["messages"]:
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
        response['data']['stw']['image'] = f"https://api.peely.de/cdn/unique/stwnews_{lang}.gif"
    except:
        traceback.print_exc()

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
