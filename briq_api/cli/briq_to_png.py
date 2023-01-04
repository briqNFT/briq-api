
if __name__ != "__main__":
    print("ERROR - need to be run as a script")
    exit(1)

import argparse
import json
from briq_api.mesh.briq import BriqData
from PIL import Image

parser = argparse.ArgumentParser(description='Convert briq JSON to PNG image.')
parser.add_argument('file', help='input briq')
args = parser.parse_args()

try:
    briqs = []

    x_axis = 0
    y_axis = 1

    multiplier = 8

    briqData = BriqData().load_file(args.file)

    x0 = x1 = None
    y0 = y1 = None
    for briq in briqData.briqs:
        if x0 is None or briq['pos'][x_axis] < x0:
            x0 = briq['pos'][x_axis]
        if y0 is None or briq['pos'][y_axis] < y0:
            y0 = briq['pos'][y_axis]
        if x1 is None or briq['pos'][x_axis] > x1:
            x1 = briq['pos'][x_axis]
        if y1 is None or briq['pos'][y_axis] > y1:
            y1 = briq['pos'][y_axis]

    image = Image.new('RGBA', (x1 - x0 + 1, y1 - y0 + 1))

    pixelMap = image.load()
    for briq in briqData.briqs:
        col = briq['data']['color']
        x = briq['pos'][x_axis]
        y = briq['pos'][y_axis]
        pixelMap[x - x0, y - y0] = (*[int(col[1 + i*2 : 1 + (i+1) * 2], 16) for i in [0, 1, 2]], 255)
    image = image.resize((image.width * multiplier, image.height * multiplier), Image.Resampling.NEAREST)
    image.save(args.file.replace("json","png"))
except Exception as err:
    print("Error running conversion of ", args.file)
    raise err
