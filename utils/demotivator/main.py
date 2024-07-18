
from PIL import Image, ImageDraw, ImageFont

from utils.const import ConstObject
from utils.funcs import joinPath

const = ConstObject()

def getDemotivator(image, text, resultName='result'):
    print(text)
    font = ImageFont.truetype(joinPath(const.path.demotivator, const.dem.fontPath), 48)
    with Image.open(joinPath(const.path.demotivator, const.dem.backgroundPath)) as backgroundPIL:
        backgroundPIL.load()
        imagePIL = Image.open(image)
        imagePIL.load()
        backgroundPIL.paste(imagePIL.resize((800, 640)), (75, 46))
        if text:
            draw = ImageDraw.Draw(backgroundPIL)
            draw.text((950 // 2, 770), text, fill=const.dem.textColor, anchor='ms', font=font)
        demotivatorPath = joinPath(const.path.cache, f'{resultName}.png')
        backgroundPIL.save(demotivatorPath, 'PNG')
    return demotivatorPath