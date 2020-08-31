import asyncio
import json
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response
from discord.ext import commands, tasks

from API.v1.comics import handler as comics
from API.v1.news import handler as news
from API.v1.news.br import handler as br_news
from API.v1.news.creative import handler as creative_news
from API.v1.news.stw import handler as stw_news
from API.v1.notices import handler as notices
from API.v1.playlists import handler as playlists
from API.v1.shop import generaterequest as generateshop
from API.v1.shop import handler as shop
from API.v1.shop.custom import handler as customshop
from API.v1.tournaments import handler as tournaments
from API.cdn import handler as cdn

client = commands.Bot(command_prefix=">")
app = sanic.app.Sanic('api')

app.add_route(cdn, "/cdn/<folder>/<name>")
app.add_route(news, "/v1/news")
app.add_route(br_news, "/v1/br/news")
app.add_route(creative_news, "/v1/creative/news")
app.add_route(stw_news, "/v1/stw/news")
app.add_route(notices, "/v1/notices")
app.add_route(tournaments, "/v1/tournaments")
app.add_route(playlists, "/v1/playlists")
app.add_route(comics, "/v1/comics")
app.add_route(shop, "/v1/shop")
app.add_route(customshop, "/v1/shop/custom")


@client.event
async def on_ready():
    try:
        check_changes.start()
    except:
        check_changes.stop()
        check_changes.start()


@tasks.loop(seconds=20)
async def check_changes():
    async with aiohttp.ClientSession() as ses:
        async with ses.get("https://fortnite-api.com/v1/shop/br") as response:
            if response.status != 200:
                return
            else:
                new = await response.json()
                old = json.loads(await (await aiofiles.open(f'Cache/data/shop.json', mode='r')).read())
                if new != old:
                    await generateshop(new, client)

@app.route('/')
async def home(req):
    return sanic.response.text('Soon')


@app.route('/favicon.ico')
async def favicon(req):
    return await sanic.response.file('favicon.ico')


loop = asyncio.get_event_loop()
loop.create_task(app.create_server(host="0.0.0.0", port=80, return_asyncio_server=True, access_log=False))
loop.create_task(client.start("NzQ5NjI5MTM1ODQzODg1MDc3.X0uwiQ.s15nVHqKS34JLWulEdhZsWTKN14"))
try:
    loop.run_forever()
except:
    pass
finally:
    loop.stop()
