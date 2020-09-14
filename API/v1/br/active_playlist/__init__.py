import pathlib

import aiofiles
import aiohttp
import sanic
import sanic.response
import random
import modules.stats
import os
import json


async def handler(req):
    await modules.stats.updatestats(req)
    lang = 'en'
    for i in req.query_args:
        if i[0] == 'lang':
            lang = str(i[1])
    playlist = json.loads(await (await aiofiles.open(f"Cache/playlistdata_{lang}.json", mode='r', encoding="utf8")).read())
    templist = []
    for path in pathlib.Path("Cache/ini").iterdir():
        if path.is_file():
            if str(path).endswith("DefaultGame.ini"):
                content = await (await aiofiles.open(path, mode='r', encoding="utf8")).read()
                for line in str(content).splitlines():
                    if line.startswith("+FrontEndPlaylistData"):
                        line = line.replace("+FrontEndPlaylistData=(PlaylistName=", "")
                        line = line.split(",")[0]
                        for i in playlist["modes"]:
                            if i['id'] == "Tutorial":
                                continue
                            if i["id"] == line.split("_")[1]:
                                ist=False
                                for i2 in templist:
                                    if i2['id'] == i['id']:
                                        ist=True
                                if ist is False:
                                    del i['enabled']
                                    del i['gameType']
                                    del i['largeTeams']
                                    del i['maxTeamSize']
                                    templist.append(i)
    response = {
        'status': 200,
        'message': 'Everything should work fine',
        'data': {
            'playlists': templist,
        }
    }
    return sanic.response.json(response)
