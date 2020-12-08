import traceback
from datetime import datetime

import dateutil.parser as dp
import sanic
import sanic.response
from PIL import Image, ImageDraw, ImageFont


async def handler(req):
    color = (235, 52, 204)
    seasonstart="2020-12-01T08:00:00Z"
    seasonend="2021-03-15T08:00:00Z"
    # seasonend=  "2020-12-12T08:00:00Z"


    daysgone = int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400)
    seasonlen= int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)

    finalim = Image.open("API/v1/br/progress/new.png")
    im = Image.open('Cache/progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    for i in range(im.height):
        if i < 5:
            continue
        if i > im.height-5:
            continue

        draw.line((5, i) + (int((754/100) * (seasonlen/100) * daysgone), i), fill=128)

    finalim.paste(im, (int((finalim.width-im.width)/2), int((finalim.height-im.height)/2)+30))
    finalim.save('cdn/current/progress.png')

    return await sanic.response.file(f'cdn/current/progress.png')
