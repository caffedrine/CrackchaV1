import requests
import traceback
import logging
import os
import shutil
import glob
from natsort import natsorted
import imagehash
from PIL import Image

import Creds
import ImageFilter
import ImageSpliter


sessGlob = None

def get_hackthis_session():
    if sessGlob is None:
        sess = requests.session()
        response = sess.post("https://www.hackthis.co.uk/?login", data={"username": Creds.username, "password": Creds.password})
        sess.get("https://www.hackthis.co.uk/levels/captcha/1")
        return sess
    else:
        return sessGlob


def get_captcha():
    sess = get_hackthis_session()
    response = sess.get("https://www.hackthis.co.uk/levels/extras/captcha1.php")
    with open("captcha.png", "wb") as fd:
        fd.write(response.content)


def fetch_training_data():
    for i in range(0, 30):
        get_captcha()
        ImageFilter.clean("captcha.png")
        ImageSpliter.ImgSplit("captcha_clean.png", "traindata")
        os.remove("captcha.png")
        os.remove("captcha_clean.png")


def make_clean():
    folder = 'guessdata'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    try:
        os.remove("captcha.png")
        os.remove("captcha_clean.png")
    except:
        pass

# sess = requests.session()
# response = sess.post("https://www.hackthis.co.uk/?login", data={"username": "ceapa", "password": "qwerty123"})
#
# sess.get("https://www.hackthis.co.uk/levels/captcha/1")
# response = sess.get("https://www.hackthis.co.uk/levels/extras/captcha1.php")
#
# with open("captcha.png", "wb") as fd:
#     fd.write(response.content)

try:

    while True:
        # Clean guessdata directory
        make_clean()

        # Fetch a new captcha
        get_captcha()

        # Remove black background from image
        ImageFilter.clean("captcha.png")

        # Split every char of the image
        # ImageSpliter.ImgSplit("captcha_clean.png", "guessdata")

        # Recognize chars
        # for letter_image in natsorted(glob.glob("guessdata/*.png")):
        #     digest1 = imagehash.phash(Image.open(letter_image))
        # for letter_image2 in glob.glob("traindata/*.png"):
        #     digest2 = imagehash.phash(Image.open(letter_image2))
        #     if digest1 == digest2:
        #         letter = os.path.basename(letter_image2)[0]
        #         print(letter, end='')
        #         break
        # else:
        #     print('8', end='')

        cmd = 'tesseract captcha_clean.png stdout nobatch letters_and_symbols'
        cmdResult = os.popen(cmd).read().rstrip("\n\r")
        cmdResult = cmdResult[::-1]

        sess = get_hackthis_session()
        response = sess.post("https://www.hackthis.co.uk/levels/captcha/1", data={"answer": cmdResult}).content


        if "Incomplete" not in str(response):
            print("SUCCESS!")
            break

        print(cmdResult)


except Exception as e:
    logging.error(traceback.format_exc())


