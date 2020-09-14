from PIL import Image, ImageDraw
from datetime import datetime
import dateutil.parser as dp
import sanic
import sanic.response
import random
import modules.stats

async def handler(req):
    await modules.stats.updatestats(req)
    color = (98, 211, 245)
    for i in req.query_args:
        if i[0] == 'color':
            temp = str(i[1]).replace("(", "")
            temp = temp.replace(")", "")
            temp = temp.replace(" ", "")
            tliste = []
            for t in temp.split(","):
                tliste.append(int(t))
            color = tuple(tliste)
            if not str(color).startswith("(") or not str(color).endswith(")"):
                color = (98, 211, 245)
    seasonend="2020-11-30T13:00:00Z"
    seasonstart="2020-08-27T13:00:00Z"

    # daysleft = int((dp.parse(seasonend).timestamp()-datetime.utcnow().timestamp())/86400)
    daysgone = int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400)
    seasonlen= int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)

    im = Image.open('Cache/progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    x, y, diam = (590/100) * int((seasonlen/100) * daysgone), 8, 34
    draw.ellipse([x, y, x+diam, y+diam], fill=color)

    ImageDraw.floodfill(im, xy=(14, 24), value=color, thresh=40)

    randomint=random.randint(0000000000000000000, 99999999999999999999999999)
    im.save(f'cdn/unique/progress_{randomint}.png')
    return await sanic.response.file(f'cdn/unique/progress_{randomint}.png')