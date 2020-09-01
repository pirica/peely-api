import asyncio
import json
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response
from discord.ext import commands, tasks

from API.cdn import handler as cdn
from API.v1.comics import handler as comics
from API.v1.leaks import generateleaks as generateleaks
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
    print("EVERYTHING READY")
    try:
        check_leaks_changes.start()
    except:
        check_leaks_changes.stop()
        check_leaks_changes.start()
    try:
        check_store_changes.start()
    except:
        check_store_changes.stop()
        check_store_changes.start()


@tasks.loop(seconds=20)
async def check_store_changes():
    await client.wait_until_ready()
    async with aiohttp.ClientSession() as ses:
        async with ses.get("https://fortnite-api.com/v1/shop/br") as responseshop:
            if responseshop.status != 200:
                return
            else:
                newshop = await responseshop.json()
                oldshop = json.loads(await (await aiofiles.open(f'Cache/data/shop.json', mode='r')).read())
                if newshop != oldshop:
                    await generateshop(newshop, client)


@tasks.loop(seconds=20)
async def check_leaks_changes():
    await client.wait_until_ready()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://benbotfn.tk/api/v1/newCosmetics") as responsebenfn:
            oldbenleaks = json.loads(await (await aiofiles.open(f'Cache/data/benbot_leaks.json', mode='r')).read())
            try:
                newbenleaks = await responsebenfn.json()
                print(newbenleaks)
            except:
                traceback.print_exc()
            if oldbenleaks != newbenleaks:
                if json.loads(await (await aiofiles.open(f'Cache/data/versioncache.json', mode='r')).read())["version"] != newbenleaks["currentVersion"]:
                    print("benbot updated")
                    if newbenleaks['items']:
                        await (await aiofiles.open('Cache/data/versioncache.json', mode='w+')).write(
                            json.dumps({"version": newbenleaks["currentVersion"]}, indent=2))
                        globaldata = {
                            "status": 200,
                            "data": {
                                "items": [{
                                    "id": cosmetic["id"],
                                    "name": cosmetic["name"],
                                    "description": cosmetic["description"],
                                    "type": {
                                        "value": cosmetic["shortDescription"],
                                        "displayValue": cosmetic["shortDescription"],
                                        "backendValue": cosmetic["backendType"]
                                    },
                                    "set": {
                                        "text": cosmetic["setText"],
                                    },
                                    "rarity": {
                                        "value": cosmetic["backendRarity"].split("::")[1],
                                        "displayValue": cosmetic["rarity"],
                                        "backendValue": cosmetic["backendRarity"]
                                    },
                                    "images": {
                                        "smallIcon": cosmetic["icons"]["icon"],
                                        "featured": cosmetic["icons"]["featured"],
                                        "icon": cosmetic["icons"]["icon"],
                                        "other": cosmetic["icons"]["icon"],
                                    }
                                } for cosmetic in newbenleaks["items"]]
                            }
                        }
                        await (await aiofiles.open('Cache/data/benleaks.json', mode='w+')).write(
                            json.dumps(newbenleaks, indent=2))
                        await generateleaks(data=globaldata, client=client)

        async with session.get(f"https://fortnite-api.com/v2/cosmetics/br/new") as responsefn:
            oldfnleaks = json.loads(await (await aiofiles.open(f'Cache/data/fnleaks.json', mode='r')).read())
            try:
                newfnleaks = await responsefn.json()
                print(newfnleaks)
            except:
                traceback.print_exc()
            if oldfnleaks != newfnleaks:
                if json.loads(await (await aiofiles.open(f'Cache/data/versioncache.json', mode='r')).read())["version"] != newfnleaks["data"]["build"]:
                    print("FN API updated")
                    await (await aiofiles.open('Cache/data/versioncache.json', mode='w+')).write(
                        json.dumps({"version": newfnleaks["data"]["build"]}, indent=2))
                    globaldata = {
                        "status": 200,
                        "data": {
                            "items": [
                            ]
                        }
                    }
                    for cosmetic in newfnleaks["data"]["items"]:
                        cosmetic["rarity"] = {
                            "value": cosmetic["rarity"]["value"],
                            "displayValue": cosmetic["rarity"]["displayValue"],
                            "backendValue": cosmetic["rarity"]["backendValue"]
                        }
                        globaldata["data"]["items"].append(cosmetic)
                    await (await aiofiles.open('Cache/data/fnleaks.json', mode='w+')).write(
                        json.dumps(newfnleaks, indent=2))
                    await generateleaks(data=globaldata, client=client)


@app.route('/')
async def home(req):
    return sanic.response.text('Soon')


@app.route('/favicon.ico')
async def favicon(req):
    return await sanic.response.file('favicon.ico')


loop = asyncio.get_event_loop()
loop.create_task(app.create_server(host="0.0.0.0", port=80, return_asyncio_server=True, access_log=False))
loop.create_task(client.run("NzQ5NjI5MTM1ODQzODg1MDc3.X0uwiQ.s15nVHqKS34JLWulEdhZsWTKN14"))
try:
    loop.run_forever()
except:
    pass
finally:
    loop.stop()
