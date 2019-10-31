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
        response = sess.post("https://www.hackthis.co.uk/?login", data={"username": Creds.username, "password": Creds.password}, timeout=20)
        sess.get("https://www.hackthis.co.uk/levels/captcha/1", timeout=20)
        return sess
    else:
        return sessGlob


def get_captcha(outputPathName = None):
    sess = get_hackthis_session()
    response = sess.get("https://www.hackthis.co.uk/levels/extras/captcha1.php", timeout=20)
    if outputPathName is not None:
    	with open(outputPathName, "wb") as fd:
        	fd.write(response.content)
    else:
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


def get_user_solution(captchaName):
	while True:
		data = input("Please enter solution for '%s': " % (captchaName))
		if len(data) < 10:
		   	print("Value too short. Please inser all captcha chars!")
		else:
			return data.rstrip("\n\r")


def build_training_data():
    counter = 0
    while True:
        i = 0
    	# Get neax available captcha directory name
        while os.path.exists('traindata/captcha' + str(i)):
            i += 1
		
		# create a new dir 
        os.makedirs('traindata/captcha' + str(i))

    	# Captcha paths
        captcha_path = "traindata/captcha%s/0_captcha%s.png" % (str(i), str(i))	
        captcha_clean_path = "traindata/captcha%s/0_captcha%s_clean.png" % (str(i), str(i))

        # Download captcha
        get_captcha( captcha_path )

    	# Remove black background from image
        ImageFilter.clean(captcha_path, captcha_clean_path)

		# Ask user for solution of current captcha
        solution = get_user_solution(captcha_path)

        # Split captcha in chars and ask for solution
        splitStatus = ImageSpliter.ImgSplit(captcha_clean_path, solution)


def main():
	# build_training_data()

    # Clean guessdata directory
    make_clean()

    # Fetch a new captcha
    get_captcha("guessdata/captcha.png")

    # Remove black background from image
    ImageFilter.clean("guessdata/captcha.png", "guessdata/captcha_clean.png")

    # Split every char of the image
    ImageSpliter.ImgSplit("guessdata/captcha_clean.png")

    # Recognize chars
    solution = ""
    for letter_image in natsorted(glob.glob("guessdata/*.png")):
        if "captcha" in letter_image:
    	    continue
        digest1 = imagehash.phash(Image.open(letter_image))
        for letter_image2 in glob.glob("traindata/**/*.png"):
            digest2 = imagehash.phash(Image.open(letter_image2))
            if digest1 == digest2:
                letter = (os.path.basename(letter_image2).split("_")[0])
                if letter in ImageSpliter.ILLEGAL_SYMBOLS.values():
                    letter =  list(ImageSpliter.ILLEGAL_SYMBOLS.keys())[list(ImageSpliter.ILLEGAL_SYMBOLS.values()).index( letter )]  
                solution += letter
                break
        else:
            solution += "8"

    print("Submitting solution: '%s' " % (solution) )
    sess = get_hackthis_session()
    response = sess.post("https://www.hackthis.co.uk/levels/captcha/1", data={"answer": solution}, timeout=20).content
    if "Incomplete" not in str(response):
        print("SUCCESS!")
    else:
        print("FAILED!")


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
	    logging.error(traceback.format_exc())


