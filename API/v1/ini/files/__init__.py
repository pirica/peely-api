import aiofiles
import sanic
import sanic.response

from modules.stats import updatestats


async def handler(req, file):
    await updatestats(req)
    try:
        return sanic.response.text(await (await aiofiles.open(f'Cache/ini/{file}', mode='r', encoding="utf8")).read())
    except:
        return sanic.response.empty(status=404)
