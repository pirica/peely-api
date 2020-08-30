import json
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response


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
                response['platform_motds'][platform['platform']] = []
            for platform_motds in data['creativenews']['news']['platform_motds']:
                response['platform_motds'][platform_motds['platform']].append({
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

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
