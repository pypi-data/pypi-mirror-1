from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from StringIO import StringIO

# Change these values to match your needs
cert_file = '/home/apyb/certificado2009.png'
font_file = '/home/apyb/verdana.ttf'

def generate(name, role):

    img = Image.open(cert_file)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_file, 128)

    pos = 1750, 1620
    draw.text(pos, name, font=font)

    pos = 3500 ,2230
    draw.text(pos, role, font=font)

    output = StringIO()
    img.save(output, format='PNG')

    return output.getvalue()

if __name__ == '__main__':
    print generate('Dorneles Tremea', 'participante')
