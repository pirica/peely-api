import json

import aiofiles
import sanic
import sanic.response

from modules.stats import updatestats


async def handler(req):
    await updatestats(req)
    return sanic.response.json(json.loads(await (await aiofiles.open(f'Cache/data/ini.json', mode='r')).read()))
