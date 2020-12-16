import traceback
from datetime import datetime

import dateutil.parser as dp
import sanic
import sanic.response
from PIL import Image, ImageDraw, ImageFont


async def handler(req):
    seasonstart="2020-12-01T08:00:00Z"
    seasonend="2021-03-15T08:00:00Z"

    daysgone = int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400)
    seasonlen= int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)

    finalim = Image.open("API/v1/br/progress/FixedBar.png")
    im = Image.open('Cache/progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    for i in range(im.height):
        if i < 5:
            continue
        if i > im.height-5:
            continue

        draw.line((5, i) + (int((754/100) * (100/seasonlen) * daysgone), i), fill=128)

    finalim.paste(im, (int((finalim.width-im.width)/2), int((finalim.height-im.height)/2)+7))
    finalim.save('cdn/current/progress.png')

    return await sanic.response.file(f'cdn/current/progress.png')
