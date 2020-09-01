import sanic
import sanic.response


async def handler(req, folder, name):
    try:
        return await sanic.response.file(f"cdn/{folder}/{name}")
    except:
        return sanic.response.empty(status=404)
