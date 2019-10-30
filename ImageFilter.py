#!/usr/bin/python3
from PIL import ImageFile
import sys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BACKG = (30, 30, 30)
GREEN = (0, 128, 0)

THRESHOLD = 150


def distance(pixel, color):
    distance = 0
    for i in range(3):
        distance += pow(color[i] - pixel[i], 2)
    return distance


def is_green(pixel):
    distance_to_green = distance(pixel, GREEN)
    if distance_to_green < THRESHOLD:
        return True
    return False


def clean(imgPath, imgOutput):
    with open(imgPath, "rb") as fd:
        p = ImageFile.Parser()
        p.feed(fd.read())
        image = p.close()

        img2 = image.copy()
        w, h = image.size

        y_start = 0xFFFF
        y_end = 0
        x_start = 0xFFFF
        x_end = 0

        for x in range(0, w):
            for y in range(0, h):
                if is_green(image.getpixel((x, y))):
                    img2.putpixel((x, y), BLACK)
                    x_start = min(x, x_start)
                    y_start = min(y, y_start)
                    x_end = max(x, x_end)
                    y_end = max(y, y_end)
                else:
                    img2.putpixel((x, y), WHITE)

        # print("Box is {}/{} to {}/{}".format(x_start, y_start, x_end, y_end))

        img2 = img2.crop(box=(x_start, y_start, x_end+1, y_end))
        img2.save(imgOutput)