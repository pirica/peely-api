import json

import aiofiles
import sanic
import sanic.response
from modules import stats


async def handler(req):
    return sanic.response.json(stats.statsdata)
