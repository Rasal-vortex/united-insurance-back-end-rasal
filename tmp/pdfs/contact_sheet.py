from PIL import Image, ImageDraw
from pathlib import Path
fs=sorted(Path('tmp/pdfs').glob('fsd-page-*.png'))
thumbs=[]
for f in fs:
    im=Image.open(f).convert('RGB')
    im.thumbnail((306,396))
    canvas=Image.new('RGB',(326,424),'#dce3ea')
    canvas.paste(im,((326-im.width)//2,8))
    ImageDraw.Draw(canvas).text((12,405),f.name,fill='black')
    thumbs.append(canvas)
out=Image.new('RGB',(326*4,424*2),'white')
for i,im in enumerate(thumbs):
    out.paste(im,((i%4)*326,(i//4)*424))
out.save('tmp/pdfs/contact.png')
