import Image
import ImageDraw
import ImageFont

# Change these values to match your needs
cert_file = '/home/apyb/certificado2009.png'
font_file = '/home/apyb/verdana.ttf'

def generate(name, role):

    img = Image.open(cert)
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype(font_file, 128)

    pos = 1750, 1620
    draw.text(pos, name, font=font)

    pos = 3500 ,2230
    draw.text(pos, role, font=font)

    return img.tostring()

if __name__ == '__main__':
    print generate('Dorneles Tremea', 'participante')
