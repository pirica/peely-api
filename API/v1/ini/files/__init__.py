import aiofiles
import sanic
import sanic.response


async def handler(req, file):
    try:
        return sanic.response.text(await (await aiofiles.open(f'Cache/ini/{file}', mode='r', encoding="utf8")).read())
    except:
        return sanic.response.empty(status=404)
