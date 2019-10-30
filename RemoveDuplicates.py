# dupFinder.py
import os, sys, glob
import hashlib
from PIL import ImageFile
from PIL import ImageStat
from PIL import Image
 
def hash_image(image_path):
    img = Image.open(image_path).resize((8,8), Image.LANCZOS).convert(mode="L")
    mean = ImageStat.Stat(img).mean[0]
    return sum((1 if p > mean else 0) << i for i, p in enumerate(img.getdata()))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        folder = sys.argv[1]
        if os.path.exists(folder):
            for image1 in glob.glob( (folder + "/*.png")):
                if os.path.isfile(image1):
                	for image2 in glob.glob( (folder + "/*.png")):
                		if (hash_image(image2) == hash_image(image1)) and (image2 != image1):
                			os.remove( image2 )
                print(".", end="")
                sys.stdout.flush()              				
        else:
            print('%s is not a valid path, please verify' % folder)
            sys.exit()
    else:
        print('Usage: python dupImgFinder.py folder or python dupFinder.py folder1 folder2 folder3')
