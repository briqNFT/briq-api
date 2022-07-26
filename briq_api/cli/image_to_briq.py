
if __name__ != "__main__":
    print("ERROR - need to be run as a script")
    exit(1)

import argparse
import json
from briq_api.mesh.briq import BriqData

parser = argparse.ArgumentParser(description='Convert PNG image to briq JSON')
parser.add_argument('file', help='input image')
args = parser.parse_args()

try:
    briqs = []
    preco = 13
    from PIL import Image
    with Image.open(args.file) as im:
        im = im.convert('RGBA')
        for x in range(0, im.width, preco):
            for y in range(0, im.height, preco):
                pixel = im.getpixel((x, y))
                briqs.append({
                    "pos": (x//preco, 0, y//preco),
                    "data": {
                        "color": '#{:02x}{:02x}{:02x}'.format(*pixel),
                        "material": "0x1"
                    }
                })
    
    with open(args.file.replace('.png', '.json'), 'w') as outf:
        json.dump({
            "name": args.file,
            "regionSize": 10,
            "version": 1,
            "briqs": briqs
        }, outf)
                
except Exception as err:
    print("Error running conversion of ", args.file)
    raise err
