import json

import aiofiles
import sanic
import sanic.response


async def handler(req):
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/data/ini.json', mode='r')).read()))
