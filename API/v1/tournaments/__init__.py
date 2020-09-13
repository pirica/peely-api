import json

import aiofiles
import aiohttp
import sanic
import sanic.response

from modules import stats


async def handler(req):
    await stats.updatestats(req)
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
            'tournaments': [],
        }
    }

    try:
        if data['tournamentinformation']['tournament_info']['tournaments']:
            for tournament in data['tournamentinformation']['tournament_info']['tournaments']:
                try:
                    response['data']['tournaments'].append({
                        'name': tournament['long_format_title'],
                        'description': tournament['details_description'],
                        'short_description': tournament["flavor_description"],
                        'id': tournament['tournament_display_id'],
                        'image': tournament['poster_front_image'],
                        'thumbnail': tournament['playlist_tile_image'],
                    })
                except:
                    continue
    except KeyError as ex:
        print(ex)

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
