import json

import aiofiles

statsdata = {}


async def updatestats(req):

    try:
        url = str(str(req.url).split("/v1/")[1]).split("?")[0]
        if url.startswith("ini/files"):
            return
        try:
            statsdata[url] += 1
        except:
            statsdata[url] = 1
    except:
        return


async def savestats():
    await (await aiofiles.open('Cache/data/apistats.json', mode='w+')).write(
        json.dumps(statsdata, indent=2))


async def rewrite():
    global statsdata
    statsdata = json.loads(await (await aiofiles.open(f'Cache/data/apistats.json', mode='r')).read())