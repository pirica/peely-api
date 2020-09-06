import io

import aiofiles
import aiohttp
from PIL import Image, ImageFont, ImageDraw


def GetMiddle(x, y):
    return (x - y) / 2


def GetBlendColor(Rarity):
    if Rarity == "frozen":
        blendColor = (148, 223, 255)
    elif Rarity == "lava":
        blendColor = (234, 141, 35)
    elif Rarity == "legendary":
        blendColor = (211, 120, 65)
    elif Rarity == "dark":
        blendColor = (251, 34, 223)
    elif Rarity == "starwars":
        blendColor = (231, 196, 19)
    elif Rarity == "marvel":
        blendColor = (197, 51, 52)
    elif Rarity == "dc":
        blendColor = (84, 117, 199)
    elif Rarity == "icon":
        blendColor = (54, 183, 183)
    elif Rarity == "shadow":
        blendColor = (113, 113, 113)
    elif Rarity == "epic":
        blendColor = (177, 91, 226)
    elif Rarity == "rare":
        blendColor = (73, 172, 242)
    elif Rarity == "uncommon":
        blendColor = (96, 170, 58)
    elif Rarity == "common":
        blendColor = (190, 190, 190)
    elif Rarity == "slurp":
        blendColor = (17, 189, 240)
    else:
        blendColor = (255, 255, 255)

    return blendColor


async def GenerateShopImage(Store: dict, background_user: str = "http://peely.de/api/background.jpg",
                            text: str = "Fortnite Item Shop"):
    # Featured items
    FeaturedItems = [Item for Item in Store["featured"] for Item in Item["items"]]
    FeaturedIDs = [ID["id"] for ID in FeaturedItems]
    FeaturedItemsCount = len(Store["featured"])

    F_Lines = 1
    F_Height = (545 * F_Lines) + 20
    F_Width = (300 * FeaturedItemsCount) + 20
    while F_Width > F_Height:
        F_Lines += 1
        F_ImagesPerLine = round(((FeaturedItemsCount) / F_Lines) + 0.49)
        F_Height = (545 * F_Lines) + 20
        F_Width = (300 * F_ImagesPerLine) + 20
    while ((F_Lines * F_ImagesPerLine) - FeaturedItemsCount) > F_ImagesPerLine or (
            (F_Lines * F_ImagesPerLine) - FeaturedItemsCount) == F_ImagesPerLine:
        F_Lines -= 1
        F_Height = (545 * F_Lines) + 20
        F_Width = (300 * F_ImagesPerLine) + 20

    # Daily items
    DailyItems = [Item for Item in Store["daily"] for Item in Item["items"]]
    DailyIDs = [ID["id"] for ID in DailyItems]
    DailyItemsCount = len(Store["daily"])

    D_Lines = 1
    D_Height = (545 * D_Lines)
    D_Width = (300 * DailyItemsCount)

    while D_Width > D_Height and D_Lines < F_Lines:
        D_Lines += 1
        D_ImagesPerLine = round(((DailyItemsCount) / D_Lines) + 0.49)
        D_Height = (545 * D_Lines)
        D_Width = (300 * D_ImagesPerLine)

    while ((D_Lines * D_ImagesPerLine) - DailyItemsCount) > D_ImagesPerLine or (
            (D_Lines * D_ImagesPerLine) - DailyItemsCount) == D_ImagesPerLine:
        D_Lines -= 1
        D_Height = (545 * D_Lines)
        D_Width = (300 * D_ImagesPerLine)

    # Count free items
    FreeItems = len([Item["finalPrice"] for Item in Store["featured"] if Item["finalPrice"] == 0]) + len(
        [Item["finalPrice"] for Item in Store["daily"] if Item["finalPrice"] == 0])

    # Open Background
    async with aiohttp.ClientSession() as session:
        async with session.get(background_user) as resp:
            if resp.status == 200:
                f = await aiofiles.open('assets/cache/temp.png', mode='wb')
                await f.write(await resp.read())
                await f.close()
                Background = Image.open(
                    io.BytesIO(await (await aiofiles.open("assets/cache/temp.png", mode='rb')).read())).resize(
                    (int(F_Width + D_Width + 20 + 50), int(F_Height + 510)),
                    Image.ANTIALIAS)
    Draw = ImageDraw.Draw(Background)
    Burbank = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 100)

    # Adspace
    NewsAdpsace = Image.open(
        io.BytesIO(await (await aiofiles.open("assets/Images/T_newPVP_Texture.png", mode='rb')).read()))
    AdspaceFont = ImageFont.truetype('assets/Fonts/BurbankBigCondensed-Black.otf', 32)

    def Adspace(X, Y, SpaceText):
        X -= 14
        Y -= 14

        AdspaceLeft = NewsAdpsace.crop((0, 0, 23, 50))
        AdspaceMiddle = NewsAdpsace.crop((23, 0, 66, 50)).resize((AdspaceFont.getsize(SpaceText)[0] - 15, 50),
                                                                 Image.ANTIALIAS)
        AdspaceRight = NewsAdpsace.crop((66, 0, 100, 50))

        Background.paste(AdspaceLeft, (X, Y), AdspaceLeft)
        Background.paste(AdspaceMiddle, (X + AdspaceLeft.width, Y), AdspaceMiddle)
        Background.paste(AdspaceRight, (X + AdspaceLeft.width + AdspaceMiddle.width, Y), AdspaceRight)
        AdspaceLeft = NewsAdpsace.crop((0, 0, 21, 50))

        Draw.text((X + AdspaceLeft.width - 3, Y + 4), SpaceText, font=AdspaceFont)

    # Pasting items
    currentHeight = 510
    currentWidth = 20
    Price = 0

    # Paste Featured
    for Item in Store["featured"]:
        card = await GenerateStoreCard(Item)
        Background.paste(card, (currentWidth, currentHeight))
        Price += Item["finalPrice"]
        if Item["banner"]:
            Adspace(currentWidth, currentHeight, Item["banner"])
        currentWidth += 300
        if F_Width == currentWidth:
            currentWidth = 20
            currentHeight += 545

    dailyStarts = F_Width + 50
    D_Width = Background.width - 20
    currentWidth = dailyStarts
    currentHeight = 510
    # Paste Daily
    for Item in Store["daily"]:
        card = await GenerateStoreCard(Item)
        Background.paste(card, (currentWidth, currentHeight))
        Price += Item["finalPrice"]
        if Item["banner"]:
            Adspace(currentWidth, currentHeight, Item["banner"])
        currentWidth += 300
        if D_Width == currentWidth:
            currentWidth = dailyStarts
            currentHeight += 545

    # Draw Featured and Daily
    FMiddle = GetMiddle(F_Width, Burbank.getsize("Featured")[0])
    Draw.text((FMiddle + 20, 350), "Featured", (255, 255, 255), font=Burbank)
    DMiddle = GetMiddle(Background.width - 20 - dailyStarts, Burbank.getsize("Daily")[0])
    Draw.text((DMiddle + dailyStarts, 350), "Daily", (255, 255, 255), font=Burbank)
    # # Draw date
    # now = datetime.now().strftime('%A %d %B %Y')
    # Middle = GetMiddle(Background.width, Burbank.getsize(now)[0])
    # Draw.text((Middle, 190), now, (255, 255, 255), font=Burbank)
    # Draw Fortnite Item Shop
    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 200)
    Middle = GetMiddle(Background.width, BurbankBigCondensed.getsize(str(text))[0])
    Draw.text((Middle, 125), str(text), (255, 255, 255), font=BurbankBigCondensed)

    return Background


async def GenerateCard(Item):
    card = Image.new("RGBA", (300, 545))
    Draw = ImageDraw.Draw(card)
    Name = Item["name"]
    Rarity = Item["rarity"]
    blendColor = GetBlendColor(Rarity)
    Category = Item["type"]
    if Item["images"]["featured"]:
        Icon = Item["images"]["featured"]["url"]
    elif Item["images"]["icon"]:
        Icon = Item["images"]["icon"]["url"]
    elif Item["images"]["smallIcon"]:
        Icon = Item["images"]["smallIcon"]["url"]
    else:
        print(Item["name"] + " Image not found!")
        return card

    try:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open(f"assets/Images/card_inside_{Rarity}.png", mode='rb')).read()))
    except:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open("assets/Images/card_inside_common.png", mode='rb')).read()))
    card.paste(layer)

    # Download the Item icon
    try:
        async with aiohttp.ClientSession() as cs:
            async with cs.get(Icon) as data:
                Icon = Image.open(io.BytesIO(await data.read()))
    except Exception as ex:
        print("DOWNLOAD ITEM ICON ERROR", ex)
        pass
    if (Category == "outfit") or (Category == "emote"):
        ratio = max(285 / Icon.width, 365 / Icon.height)
    elif Category == "wrap":
        ratio = max(230 / Icon.width, 310 / Icon.height)
    else:
        ratio = max(310 / Icon.width, 390 / Icon.height)
    Icon = Icon.resize((int(Icon.width * ratio), int(Icon.height * ratio)), Image.ANTIALIAS)
    Middle = int((card.width - Icon.width) / 2)  # Get the middle of card and icon
    # Paste the image
    if (Category == "outfit") or (Category == "emote"):
        card.paste(Icon, (Middle, 0), Icon)
    else:
        card.paste(Icon, (Middle, 15), Icon)

    try:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open(f"assets/Images/card_faceplate_{Rarity}.png", mode='rb')).read()))
    except:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open("assets/Images/card_faceplate_common.png", mode='rb')).read()))
    try:
        card.paste(layer, layer)
    except:
        pass
    try:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open(f"assets/Images/card_bottom_{Rarity}.png", mode='rb')).read()))
    except:
        layer = Image.open(
            io.BytesIO(await (await aiofiles.open("assets/Images/card_bottom_common.png", mode='rb')).read()))
    try:
        card.paste(layer, layer)
    except:
        pass

    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 30)
    textWidth = BurbankBigCondensed.getsize(f"{Item['shortDescription']}")[0]

    Middle = int((card.width - textWidth) / 2)
    Draw.text((Middle, 385), f"{Item['shortDescription']}", blendColor, font=BurbankBigCondensed)

    FontSize = 56
    while ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", FontSize).getsize(Name)[0] > 265:
        FontSize -= 1

    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", FontSize)
    textWidth = BurbankBigCondensed.getsize(Name)[0]
    change = 56 - FontSize

    Middle = int((card.width - textWidth) / 2)
    Top = 425 + change / 2
    Draw.text((Middle, Top), Name, (255, 255, 0), font=BurbankBigCondensed)

    return card


async def GenerateStoreCard(Item):
    card = await GenerateCard(Item["items"][0])
    Draw = ImageDraw.Draw(card)
    blendColor = GetBlendColor(Item["items"][0]["rarity"])
    Name = Item["items"][0]["name"]

    if len(Item["items"]) > 1:
        i = 0

        for extra in Item["items"][1:]:
            try:
                extraRarity = extra["rarity"]
                extraIcon = extra["images"]["smallIcon"]["url"]
            except:
                pass

            try:
                layer = Image.open(io.BytesIO(
                    await (await aiofiles.open(f"assets/Images/box_bottom_{extraRarity}.png", mode='rb')).read()))
            except:
                layer = Image.open(
                    io.BytesIO(await (await aiofiles.open("assets/Images/box_bottom_common.png", mode='rb')).read()))
            card.paste(layer, ((card.width - (layer.width + 9)), (9 + ((i // 1) * (layer.height)))))

            # Download the icon
            try:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(extraIcon) as data:
                        extraIcon = Image.open(io.BytesIO(await data.read()))
            except Exception as ex:
                print("ERROR BEIM NORMALEN ICON", ex)
                pass
            ratio = max(75 / extraIcon.width, 75 / extraIcon.height)
            extraIcon = extraIcon.resize((int(extraIcon.width * ratio), int(extraIcon.height * ratio)), Image.ANTIALIAS)
            # Paste icon
            try:
                layer = Image.open(io.BytesIO(
                    await (await aiofiles.open(f"assets/Images/box_faceplate_{extraRarity}.png", mode='rb')).read()))
            except:
                layer = Image.open(
                    io.BytesIO(await (await aiofiles.open("assets/Images/box_faceplate_common.png", mode='rb')).read()))
            card.paste(extraIcon, ((card.width - (layer.width + 9)), (9 + ((i // 1) * (extraIcon.height))),), extraIcon)
            card.paste(layer, ((card.width - (layer.width + 9)), (9 + ((i // 1) * (layer.height)))), layer)
            i += 1

    vbucks = Image.open(io.BytesIO(await (await aiofiles.open("assets/Images/vbucks.png", mode='rb')).read()))

    if Item["finalPrice"] == 0:
        price = "Free"
    else:
        price = str(Item["finalPrice"])

    BurbankBigCondensed = ImageFont.truetype(f"assets/Fonts/BurbankBigCondensed-Black.otf", 30)

    textWidth = BurbankBigCondensed.getsize(price)[0]
    Middle = int((card.width - ((textWidth - 5) - vbucks.width)) / 2)
    Draw.text((Middle, 490), price, (255, 255, 255), font=BurbankBigCondensed)
    Middle = int((card.width - (vbucks.width + (textWidth + 5))) / 2)
    card.paste(vbucks, (Middle, 495), vbucks)

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
