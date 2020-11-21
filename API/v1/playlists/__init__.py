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
            'playlists': []
        },
    }

    try:
        if data['playlistinformation']['playlist_info']['playlists']:
            for playlist in data['playlistinformation']['playlist_info']['playlists']:
                try:
                    response['data']['playlists'].append({
                        'playlist_name': playlist['display_name'],
                        'playlist_id': playlist['playlist_name'],
                        'image': playlist['image'],
                        'description': playlist['description'],
                    })
                except KeyError:
                    try:
                        response['data']['playlists'].append({
                            'playlist_name': '',
                            'playlist_id': playlist['playlist_name'],
                            'image': playlist['image'],
                            'description': playlist['description'],
                        })
                    except KeyError:
                        try:
                            response['data']['playlists'].append({
                                'playlist_name': '',
                                'playlist_id': playlist['playlist_name'],
                                'image': playlist['image'],
                                'description': ''
                            })
                        except KeyError:
                            try:
                                response['data']['playlists'].append({
                                    'playlist_name': '',
                                    'playlist_id': playlist['playlist_name'],
                                    'image': '',
                                    'description': ''
                                })
                            except KeyError:
                                continue
    except KeyError as ex:
        print(ex)

    await (await aiofiles.open(f'Cache/content-{lang}.json', mode='w+', encoding='utf8')).write(
        json.dumps(await req.json(), indent=3))
    return sanic.response.json(response)
