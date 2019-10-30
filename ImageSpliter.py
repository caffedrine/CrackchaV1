#!/usr/bin/python3
from PIL import ImageFile
import sys
import logging
import os
import glob
import re

from natsort import natsorted

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


def ImgSplit(imgPath, solution):
    with open(imgPath, "rb") as fd:
        outputPath = os.path.dirname(imgPath)
        p = ImageFile.Parser()
        p.feed(fd.read())
        image = p.close()
     
        img2 = image.copy()
        w, h = image.size
     
        y_start = 0xFFFF
        y_end = 0
        x_start = 0xFFFF
        x_end = 0
     
        ranges = []
        start = 0
     
        for x in range(0, w):
            is_empty = True
            for y in range(0, h):
                if image.getpixel((x, y)) == BLACK:
                    is_empty = False
                    break
     
            if is_empty:
                if start < x-1:
                    ranges.append((start, x-1))
                start = x+1
     
        ranges.append((start, w-1))
        logging.debug(ranges)
        if solution and len(ranges) != len(solution):
            logging.error("Number of found boxes doesn't match solution length!")
            exit()
     
        for i, (x_start, x_end) in enumerate(ranges):
            img2 = image.crop(box=(x_start, 0, x_end+1, h))
            j = 0
            while True:
                if solution:
                    filename = outputPath"/{}_{}.png".format(solution[i], j)
                else:
                    filename = outputPath + "/{}.png".format(i)
     
                if os.path.exists(filename):
                    j += 1
                else:
                    img2.save(filename)
                    break
