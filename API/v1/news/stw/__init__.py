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
                    data = (json.loads(await (await aiofiles.open(f'Cache/content-{lang}.json', mode='r')).read()))[
                        'savetheworldnews']
                except:
                    return sanic.response.json({'status': 500, 'message': 'Intern Server error'})
            else:
                data = (await req.json())['savetheworldnews']
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
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
    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
