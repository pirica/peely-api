import json

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
                    return sanic.response.json({'status': 500, 'message': 'Intern Server error'}, status=500)
            else:
                data = (await req.json())
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'messages': [],
            'messagesv2': [],
            'platform_messages': {},
            'region_messages': {}
        }
    }

    try:
        if data["emergencynoticev2"]["news"]["messages"]:
            for message in data["emergencynoticev2"]["news"]["messages"]:
                response['data']['messages'].append({
                    'title': message['title'],
                    'body': message['body'],
                })
    except:
        pass

    try:
        if data["battleroyalenewsv2"]["news"]["emergencynotices"]:
            for message in data["battleroyalenewsv2"]["news"]["emergencynotices"]:
                response['data']['messagesv2'].append({
                    'title': message['title'],
                    'body': message['body'],
                })
    except:
        pass
    
    try:
        if data["emergencynoticev2"]["news"]["region_messages"]:
            for region in data["emergencynoticev2"]["news"]["region_messages"]:
                response['data']['platform_messages'][region['region']] = []
            for region_message in data["emergencynoticev2"]["news"]["region_messages"]:
                response['data']['platform_messages'][region_message['region']].append({
                    'title': region_message['message']['title'],
                    'body': region_message['message']['body'],
                    'spotlight': region_message['message']['spotlight'],
                    'hidden': region_message['message']['hidden'],
                    'gamemodes': region_message['message']['gamemodes'],
                })
    except:
        pass

    try:
        if data["emergencynoticev2"]["news"]['platform_messages']:
            for platform in data["emergencynoticev2"]["news"]['platform_messages']:
                response['data']['platform_messages'][platform['platform']] = []

            for platform_message in data["emergencynoticev2"]["news"]['platform_messages']:
                response['data']['platform_messages'][platform_message['platform']].append({
                    'image': platform_message['message']['image'],
                    'tileImage': platform_message['message']['tileImage'],
                    'title': platform_message['message']['title'],
                    'body': platform_message['message']['body'],
                    'id': platform_message['message']['id'],
                    'spotlight': platform_message['message']['spotlight']
                })
    except:
        pass

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
