import asyncio
import json
import traceback

import aiofiles
import aiohttp
import sanic
import sanic.response
from discord.ext import commands, tasks

from API.cdn import handler as cdn
from API.v1.blogposts.competitive import handler as competitiveblogposts
from API.v1.blogposts.normal import handler as normalblogposts
from API.v1.comics import handler as comics
from API.v1.ini import handler as ini
from API.v1.ini.files import handler as inifile
from API.v1.leaks import generateleaks as generateleaks
from API.v1.leaks import handler as leaks
from API.v1.leaks.data import handler as leaksdata
from API.v1.leaks.custom import handler as leakscustom
from API.v1.news import handler as news
from API.v1.news.br import handler as br_news
from API.v1.news.creative import handler as creative_news
from API.v1.news.stw import handler as stw_news
from API.v1.notices import handler as notices
from API.v1.playlists import handler as playlists
from API.v1.shop import generaterequest as generateshop
from API.v1.shop import handler as shop
from API.v1.shop.custom import handler as customshop
from API.v1.staging import handler as staging
from API.v1.staging import updatedevserver as updatestaging
from API.v1.tournaments import handler as tournaments

client = commands.Bot(command_prefix=">")
app = sanic.app.Sanic('api')
app.config.FORWARDED_SECRET = "api"

app.add_route(cdn, "/cdn/<folder>/<name>")
app.add_route(inifile, "/v1/ini/files/<file>")
app.add_route(ini, "/v1/ini/")
app.add_route(news, "/v1/news")
app.add_route(staging, "/v1/staging")
app.add_route(competitiveblogposts, "/v1/blogposts/competitive")
app.add_route(normalblogposts, "/v1/blogposts/normal")
app.add_route(br_news, "/v1/br/news")
app.add_route(creative_news, "/v1/creative/news")
app.add_route(stw_news, "/v1/stw/news")
app.add_route(notices, "/v1/notices")
app.add_route(leaksdata, "/v1/leaks/data")
app.add_route(leakscustom, "/v1/leaks/custom")
app.add_route(leaks, "/v1/leaks")
app.add_route(tournaments, "/v1/tournaments")
app.add_route(tournaments, "/v1/tournament")
app.add_route(playlists, "/v1/playlists")
app.add_route(comics, "/v1/comics")
app.add_route(shop, "/v1/shop")
app.add_route(customshop, "/v1/shop/custom")


@client.event
async def on_ready():
    print("EVERYTHING READY")
    try:
        check_20.start()
    except:
        check_20.stop()
        check_20.start()
    try:
        check_120.start()
    except:
        check_120.stop()
        check_120.start()


@tasks.loop(seconds=20)
async def check_20():
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
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://benbotfn.tk/api/v1/newCosmetics") as responsebenfn:
            if responsebenfn.status == 200:
                oldbenleaks = json.loads(await (await aiofiles.open(f'Cache/data/benleaks.json', mode='r')).read())
                try:
                    newbenleaks = await responsebenfn.json()
                except:
                    traceback.print_exc()
                if oldbenleaks != newbenleaks:
                    if json.loads(await (await aiofiles.open(f'Cache/data/versioncache.json', mode='r')).read()) \
                        ["version"] != newbenleaks["currentVersion"]:
                        print("benbot updated")
                        if newbenleaks['items']:
                            await (await aiofiles.open('Cache/data/versioncache.json', mode='w+')).write(
                                json.dumps({"version": newbenleaks["currentVersion"]}, indent=2))
                            globaldata = {
                                "status": 200,
                                "NOTE": "Some values can be different because the Data is compared. Use ID´s in your work",
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
    async with aiohttp.ClientSession() as ses:
        async with ses.get(f"https://fortnite-api.com/v2/cosmetics/br/new",
                           headers={"x-api-key": "0efed31895736f6cb95f9ef7742bf2891f7d155d"}) as responsefn:
            if responsefn.status == 200:
                oldfnleaks = json.loads(await (await aiofiles.open(f'Cache/data/fnleaks.json', mode='r')).read())
                try:
                    newfnleaks = await responsefn.json()
                except:
                    traceback.print_exc()
                if oldfnleaks != newfnleaks:
                    if json.loads(await (await aiofiles.open(f'Cache/data/versioncache.json', mode='r')).read()) \
                            ["version"] != newfnleaks["data"]["build"]:
                        print("FN API updated")
                        await (await aiofiles.open('Cache/data/versioncache.json', mode='w+')).write(
                            json.dumps({"version": newfnleaks["data"]["build"]}, indent=2))
                        globaldata = {
                            "status": 200,
                            "NOTE": "Some values can be different because the Data is compared. Use ID´s in your work",
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


@tasks.loop(seconds=120)
async def check_120():
    temp = []
    for i in json.loads(await (await aiofiles.open(f'Cache/data/devserverliste.json', mode='r')).read()):
        await client.wait_until_ready()
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get("https://" + i + "/fortnite/api/version") as data:
                    if data.status != 200:
                        continue
                    try:
                        temp.append(dict(await data.json())['version'])
                    except:
                        continue
        except:
            continue
    await updatestaging(temp)

    await client.wait_until_ready()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.nitestats.com/v1/epic/bearer") as resp:
            if resp.status == 200:
                await (await aiofiles.open('Cache/data/token.json', mode='w+')).write(
                    json.dumps({"token": dict(await resp.json())['accessToken']}, indent=2))

    await client.wait_until_ready()
    token = (json.loads(await (await aiofiles.open('Cache/data/token.json', mode='r', errors='ignore')).read()))[
        'token']
    async with aiohttp.ClientSession() as cs:
        headers = {"Authorization": f"bearer {token}"}
        async with cs.get(
                'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/cloudstorage/system',
                headers=headers) as data:
            if data.status == 200:
                templiste = []
                new = await data.json()
                for i in new:
                    async with aiohttp.ClientSession() as cs:
                        headers = {"Authorization": f"bearer {token}"}
                        async with cs.get(
                                f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/cloudstorage/system/{i["uniqueFilename"]}',
                                headers=headers) as data:
                            if data.status == 200:
                                async with aiofiles.open(f"Cache/ini/{i['filename']}", mode="w+",
                                                         encoding="utf8") as file:
                                    tempdata = str(await data.text())
                                    if tempdata.startswith("s"):
                                        continue
                                    templiste.append(f"{i['filename']}")
                                    await file.write(str(await data.text()))
                await (await aiofiles.open('Cache/data/ini.json', mode='w+')).write(
                    json.dumps(templiste, indent=2))


@app.route('/')
async def home(req):
    return sanic.response.redirect("https://docs.api.peely.de")


@app.route('/favicon.ico')
async def favicon(req):
    return await sanic.response.file('favicon.ico')


loop = asyncio.get_event_loop()
loop.create_task(app.create_server(host="0.0.0.0", port=1001, return_asyncio_server=True, access_log=False))
loop.create_task(client.run("NzQ5NjI5MTM1ODQzODg1MDc3.X0uwiQ.s15nVHqKS34JLWulEdhZsWTKN14"))
try:
    loop.run_forever()
except:
    pass
finally:
    loop.stop()
