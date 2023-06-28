import pytesseract
import numpy as np
import cv2 as cv
from skimage.metrics import structural_similarity
from PIL import Image, ImageFont, ImageDraw

# zoom at the word in the image and return the zoomed image
def get_zoomed(gray,shape):
    
    h,w = shape

    bimage = cv.threshold(gray,127,255,cv.THRESH_BINARY_INV)[1]

    # top
    for i in range(0,h):
        for j in range(0,w):
            if int(bimage[i][j]):
                top = i-1 if i > 0 else 0
                break
        else:
            top = 0
            continue
        break
    
    # left
    for i in range(0,w):
        for j in range(0,h):
            if int(bimage[j][i]):
                left = i-1 if i > 0 else 0
                break
        else:
            left = 0
            continue
        break
    
    # bottom
    for i in range(h-1,-1,-1):
        for j in range(0,w):
            if int(bimage[i][j]):
                bottom = i+1 if i < h-1 else h-1
                break
        else:
            bottom = h-1
            continue
        break
    
    # right
    for i in range(w-1,-1,-1):
        for j in range(0,h):
            if int(bimage[j][i]):
                right = i+1 if i < w-1 else w-1
                break
        else:
            right = w-1
            continue
        break

    cropped_img = gray[top:bottom+1,left:right+1]
    try:
        if (top < bottom and left < right ):
            cropped_img = cv.resize(cropped_img,(w,h))
        else:
            cropped_img = gray
    except:
        print(cropped_img)
        print(top,bottom,right,left)
        assert False

    return cropped_img   



class OCR():

    def __init__(self,words,langs,font_dict):
        
        self.Words = words
        self.Langs = langs # list of languages
        self.Font_dict = font_dict # dictionary of fonts with corresponding languages


    def image_to_text(self):
        texts = []
        wordcount = 0
        for word in self.Words:
            
            wordimage = word[0]
            fontsize = int(word[1][3]*3/4)
            text,lang = self.convert_to_text(wordimage,fontsize)
            texts.append([[text,lang],word[1]])
            wordcount += 1

            print("\033[K Word Finished = {}/{}\r".format(wordcount,len(self.Words)),end=" ")

        print()
        return texts
    
    def convert_to_text(self,wimg,fontsize):
        text = {}
        for lang in self.Langs:
            cfg = "-l {} --psm {}".format(lang,6) 
            text[lang] = pytesseract.image_to_string(wimg,config=cfg)[:-1]
        
        image_dict = {}

        gray_wordimg = cv.cvtColor(wimg,cv.COLOR_BGR2GRAY)
        zoomed_wordimg = get_zoomed(gray_wordimg,wimg.shape[:2])

        for key in self.Font_dict.keys():

            max_similarity= 0
            for font_path in self.Font_dict[key]:

                img = self.text_to_image(text[key],font_path,fontsize,wimg.shape[:2])
                gray_img = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
                zoomed_img = get_zoomed(gray_img,wimg.shape[:2])

                similarity = structural_similarity(zoomed_wordimg,zoomed_img)

                if (similarity > max_similarity):
                    max_similarity = similarity
            
            image_dict[key] = max_similarity
        
        lang_predicted = max(image_dict,key=image_dict.get)

        return text[lang_predicted],lang_predicted
    
    def text_to_image(self,text,font_path,fontsize,img_dim):

        font = ImageFont.truetype(font_path, size=fontsize)
        img = Image.new("RGB", (img_dim[1]+1, img_dim[0]+1),color=(255,255,255))
        draw = ImageDraw.Draw(img)
        draw.text((0,0),text,font=font,fill="black",font_align="center")

        return np.asarray(img)
    

