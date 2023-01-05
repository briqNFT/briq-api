from typing import Sequence
from PIL import Image


# Throws in case of errors
def to_png(briqs: Sequence):
    multiplier = 8

    x0 = x1 = None
    y0 = y1 = None
    z0 = z1 = None

    for briq in briqs:
        if x0 is None or briq['pos'][0] < x0:
            x0 = briq['pos'][0]
        if y0 is None or briq['pos'][1] < y0:
            y0 = briq['pos'][1]
        if z0 is None or briq['pos'][2] < z0:
            z0 = briq['pos'][2]
        if x1 is None or briq['pos'][0] > x1:
            x1 = briq['pos'][0]
        if y1 is None or briq['pos'][1] > y1:
            y1 = briq['pos'][1]
        if z1 is None or briq['pos'][2] > z1:
            z1 = briq['pos'][2]

    sizes = [x1 - x0, y1 - y0, z1 - z0]

    if max(sizes) > 2000:
        raise ValueError("Size would result in an image that's too large")

    # Find the best projection
    x_axis = 0
    x0 = x0
    y_axis = 1
    y0 = y0
    if sizes[0] < sizes[1] and sizes[0] < sizes[2]:
        x_axis = 2
        x0 = z0
    if sizes[1] < sizes[0] and sizes[1] < sizes[2]:
        y_axis = 2
        y0 = z0

    if max(sizes) > 500:
        multiplier = 1
    elif max(sizes) > 250:
        multiplier = 2
    elif max(sizes) > 125:
        multiplier = 4
    elif max(sizes) > 50:
        multiplier = 8
    elif max(sizes) > 26:
        multiplier = 16
    else:
        multiplier = 32

    image = Image.new('RGBA', (sizes[x_axis] + 1, sizes[y_axis] + 1))

    pixelMap = image.load()
    for briq in briqs:
        col = briq['data']['color']
        x = briq['pos'][x_axis]
        y = briq['pos'][y_axis]
        # y axis is flipped
        pixelMap[x - x0, sizes[y_axis] - (y - y0)] = (*[int(col[1 + i*2 : 1 + (i+1) * 2], 16) for i in [0, 1, 2]], 255)
    image = image.resize((image.width * multiplier, image.height * multiplier), Image.Resampling.NEAREST)
    return image
