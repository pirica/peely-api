import traceback
from datetime import datetime

import dateutil.parser as dp
import sanic
import sanic.response
from PIL import Image, ImageDraw, ImageFont


async def handler(req):
    lang = 'en'
    for i in req.query_args:
        if i[0] == 'lang':
            lang = str(i[1]).lower()
            if lang != "es-419":
                lang = "en"
    color = (235, 52, 204)
    seasonstart="2020-12-02T10:00:00Z"
    seasonend="2021-03-15T10:00:00Z"

    daysgone = int((datetime.utcnow().timestamp()-dp.parse(seasonstart).timestamp())/86400)
    seasonlen= int((dp.parse(seasonend).timestamp()-dp.parse(seasonstart).timestamp())/86400)

    finalim = Image.open("API/v1/br/progress/FixedBar.png")
    im = Image.open('Cache/progress.png').convert('RGB')
    draw = ImageDraw.Draw(im)

    x, y, diam = (590/100) * int((seasonlen/100) * daysgone), 8, 34
    draw.ellipse([x, y, x+diam, y+diam], fill=color)

    ImageDraw.floodfill(im, xy=(14, 24), value=color, thresh=40)

    try:
        draw = ImageDraw.Draw(finalim)

        if lang == "es-419":
            text = f"Progreso de la Temporada #5 de Fortnite: {int((daysgone / 100 * seasonlen))}% "
        else:
            text = f"Fortnite Season 5 - {int((daysgone / 100) * seasonlen)}% over"

        BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 45)
        textWidth = BurbankBigCondensed.getsize(text)[0]
        Middle = int((finalim.width - textWidth) / 2)
        draw.text((Middle, 13), text, color,
                  font=BurbankBigCondensed)
    except:
        traceback.print_exc()

    finalim.paste(im, (89, 73))
    finalim.save('cdn/current/progress.png')

    return await sanic.response.file(f'cdn/current/progress.png')
