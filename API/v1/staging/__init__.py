import json
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response

from modules import stats


async def handler(req):
    await stats.updatestats(req)
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/devserver.json', mode='r')).read()))


async def updatedevserver(data):
    try:
        response = {
            'status': 200,
            'message': 'Everything should work fine',
            'data': {
                "staging": "error"
            }
        }
        for version in data:
            if not response['data'].get(str(version)):
                response['data'][str(version)] = 0
            response['data'][str(version)] += 1
        async with aiohttp.ClientSession() as cs:
            async with cs.get("https://fortnite-public-service-stage.ol.epicgames.com/fortnite/api/version") as data:
                if data.status == 200:
                    try:
                        response['data']['staging'] = str(dict(await data.json())['version'])
                    except:
                        pass
        await (await aiofiles.open(f'Cache/devserver.json', mode='w+', encoding='utf8')).write(
            json.dumps(response, indent=3))
    except:
        traceback.print_exc()
