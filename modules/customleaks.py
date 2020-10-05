import io
import math
import traceback

import aiofiles
import aiohttp
from PIL import Image, ImageFont, ImageDraw


def GetMiddle(x, y):
    return (x - y) / 2


def GetBlendColor(Rarity):
    if Rarity.lower() == "frozen":
        return 148, 223, 255
    elif Rarity.lower() == "lava":
        return 234, 141, 35
    elif Rarity.lower() == "legendary":
        return 167, 78, 66
    elif Rarity.lower() == "dark":
        return 251, 34, 223
    elif Rarity.lower() == "starwars":
        return 231, 196, 19
    elif Rarity.lower() == "marvel":
        return 197, 51, 52
    elif Rarity.lower() == "mythic":
        return 255, 253, 112
    elif Rarity.lower() == "dc":
        return 84, 117, 199
    elif Rarity.lower() == "icon":
        return 54, 183, 183
    elif Rarity.lower() == "shadow":
        return 113, 113, 113
    elif Rarity.lower() == "epic":
        return 177, 91, 226
    elif Rarity.lower() == "rare":
        return 73, 172, 242
    elif Rarity.lower() == "uncommon":
        return 96, 170, 58
    elif Rarity.lower() == "common":
        return 190, 190, 190
    elif Rarity == "slurp":
        return 41, 150, 182
    else:
        return 255, 255, 255


async def GenerateCard(Item):
    card = Image.new("RGBA", (300, 545))
    Draw = ImageDraw.Draw(card)
    Name = Item["name"]
    Rarity = Item["rarity"]["value"].lower()
    blendColor = GetBlendColor(Rarity)
    Category = Item["type"]["value"]
    displayCategory = Item["type"]["displayValue"]

    try:
        layer = Image.open(
            io.BytesIO(
                await (await aiofiles.open(f"assets/Images/card_inside_{Rarity.lower()}.png", mode='rb')).read()))
    except Exception as ex:
        print(ex, "1121212")
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open("assets/Images/card_inside_common.png", mode='rb')).read()))
    card.paste(layer)

    if Item["images"]["featured"] is not None:
        Icon = Item["images"]["featured"]
    else:
        if Item["images"]["icon"] is not None:
            Icon = Item["images"]["icon"]
        else:
            if Item["images"]["smallIcon"] is not None:
                Icon = Item["images"]["smallIcon"]
            else:
                if Item["images"]["other"] is not None:
                    Icon = Item["images"]["other"]
                else:
                    Icon = "https://webhostingmedia.net/wp-content/uploads/2018/01/http-error-404-not-found.png"
    # Download the Item icon
    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(Icon) as data:
                Icon = Image.open(io.BytesIO(await data.read()))
    except Exception as ex:
        print("DOWNLOAD ITEM ICON ERROR", ex)
        return
    if (Category == "outfit") or (Category == "emote"):
        ratio = max(285 / Icon.width, 365 / Icon.height)
    elif Category == "wrap":
        ratio = max(230 / Icon.width, 310 / Icon.height)
    else:
        ratio = max(310 / Icon.width, 390 / Icon.height)
    Icon = Icon.resize((int(Icon.width * ratio), int(Icon.height * ratio)), Image.ANTIALIAS)
    Icon = Icon.convert("RGBA")
    Middle = int((card.width - Icon.width) / 2)  # Get the middle of card and icon
    # Paste the image
    if (Category == "outfit") or (Category == "emote"):
        card.paste(Icon, (Middle, 0), Icon)
    else:
        card.paste(Icon, (Middle, 15), Icon)

    try:
        layer = Image.open(
            io.BytesIO(
                await (await aiofiles.open(f"assets/Images/card_faceplate_{Rarity.lower()}.png", mode='rb')).read()))
        card.paste(layer, layer)
    except Exception as ex:
        print(ex, "233232332")
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open("assets/Images/card_faceplate_common.png", mode='rb')).read()))
        card.paste(layer, layer)
    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 30)
    textWidth = BurbankBigCondensed.getsize(f"{displayCategory.capitalize()}")[0]

    Middle = int((card.width - textWidth) / 2)
    Draw.text((Middle, 385), f"{displayCategory.capitalize()}", blendColor,
              font=BurbankBigCondensed)

    FontSize = 56
    while ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", FontSize).getsize(Name)[0] > 265:
        FontSize -= 1

    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", FontSize)
    textWidth = BurbankBigCondensed.getsize(Name)[0]
    change = 56 - FontSize

    Middle = int((card.width - textWidth) / 2)
    Top = 425 + change / 2
    Draw.text((Middle, Top), Name, (255, 255, 255), font=BurbankBigCondensed)

    return card


async def generate(Leaks: dict, background: str = "http://peely.de/api/background.jpg", text: str = "Fortnite Leaks"):
    files = []
    for i in Leaks["data"]['items']:
        try:
            files.append(await GenerateCard(i))
        except Exception as ex:
            traceback.print_exception(type(ex), ex, ex.__traceback__)
            continue
    if not files:
        return
    result = Image.new("RGB", (
        round(math.sqrt(len(files)) + 0.45) * 305 - 5, (round(math.sqrt(len(files)) + 0.45) * 550 - 5)+375))

    async with aiohttp.ClientSession() as session:
        async with session.get(background) as resp:
            if resp.status == 200:
                f = await aiofiles.open('assets/cache/temp.png', mode='wb')
                await f.write(await resp.read())
                await f.close()
                Background = Image.open(
                    io.BytesIO(await (
                        await aiofiles.open("assets/cache/temp.png", mode='rb')).read())).resize((int(
                    round(math.sqrt(len(files)) + 0.45) * 305 - 5), int(
                    (round(math.sqrt(len(files)) + 0.45) * 550 - 5)+375)), Image.ANTIALIAS)

    result.paste(Background)
    Draw = ImageDraw.Draw(result)
    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 200)
    Middle = GetMiddle(Background.width, BurbankBigCondensed.getsize(str(text))[0])
    Draw.text((Middle, 100), str(text), (255, 255, 255), font=BurbankBigCondensed)
    x = -305
    y = 400
    count = 0
    for img in files:
        try:
            img.thumbnail((305, 550), Image.ANTIALIAS)
            img.convert("RGB")
            w, h = img.size
            if count >= round(math.sqrt(len(files)) + 0.45):
                y += 550
                x = -305
                count = 0
            x += 305
            count += 1
            result.paste(img, (x, y, x + w, y + h))
        except:
            continue
    return result
