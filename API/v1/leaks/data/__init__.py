import json

import aiofiles
import aiohttp
import sanic
import sanic.response


async def handler(req):
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/data/leaks.json', mode='r')).read()))