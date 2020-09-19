import io
import traceback

import aiofiles
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import dateutil.parser as dp
import sanic
import sanic.response
import random
import modules.stats
import PIL

async def handler(req):
    await modules.stats.updatestats(req)
    color = (255, 255, 0)
    seasonend="2020-11-30T13:00:00Z"
    seasonstart="2020-08-27T13:00:00Z"

    # daysleft = int((dp.parse(seasonend).timestamp()-datetime.utcnow().timestamp())/86400)
    daysgone = int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400)
    seasonlen= int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)

    finalim = Image.open("API/v1/br/progress/new.png")
    im = Image.open('Cache/progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    x, y, diam = (590/100) * int((seasonlen/100) * daysgone), 8, 34
    draw.ellipse([x, y, x+diam, y+diam], fill=color)

    ImageDraw.floodfill(im, xy=(14, 24), value=color, thresh=40)

    try:
        draw = ImageDraw.Draw(finalim)
        text = f"{int((seasonlen/100) * daysgone)}"


        if len(text) >= 3:
            BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 40)
            textWidth = BurbankBigCondensed.getsize(text)[0]
            Middle = int((finalim.width - textWidth) / 2)
            draw.text((Middle + 95, 15), text, color,
                      font=BurbankBigCondensed)
        else:
            BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45)
            textWidth = BurbankBigCondensed.getsize(text)[0]
            Middle = int((finalim.width - textWidth) / 2)
            draw.text((Middle + 100, 13), text, color,
                      font=BurbankBigCondensed)
    except:
        traceback.print_exc()

    finalim.paste(im, (89, 73))
    finalim.save('cdn/current/progress.png')

    return await sanic.response.file(f'cdn/current/progress.png')