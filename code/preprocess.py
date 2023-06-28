import pytesseract 
from pytesseract import Output
import cv2 as cv
import numpy as np
import os

class Preprocess():

    # Initialization
    def __init__(self,page_dir,word_dir,preprocessed_img_dir,gap=4,overlap_ratio = 0.8,saveword=False,savePreprocessedImage=True):

        # read input
        self.PAGE_DIR = page_dir

        # output segmented word
        self.WORD_DIR = word_dir

        # gap allowed between two letters (should be less than gap between words)
        self.GAP = gap

        # preprocessed page 
        self.PREPROCESSED_DIR = preprocessed_img_dir

        # if two bounding box overlap more than overlap_ratio, take the smaller one (better chance of getting word)
        self.OVERLAP_RATIO = overlap_ratio

        # want to save words
        self.SaveWord = saveword
        self.WordCount = 1

        # save preprocessed images
        self.SavePreprocessedImage = savePreprocessedImage

    # return words which are array([img_of_word,bounding_box])
    def __getitem__(self,pagenum):

        # preprocess image (get binary,grayscale) image
        status = self.imagepreprocessing(pagenum)

        # if no such image exist
        if not status:
            print("Page Number Invalid")
            return []
        
        # get all the boxes in the page
        bboxes = self.generate_boxes()

        # separate the word boxes, horizontal lines, vertical lines (each are array([x,y,w,h]))
        self.horizontal_lines,self.vertical_lines,self.bboxes = self.filter(bboxes)

        
        # get image of each word box 
        words = self.get_word_arr() # words are list of 

        # save those word images in self.WORD_DIR
        if self.SaveWord:
            self.save(words)

        # display the bounding box in SELF.PREPROCESSED_DIR
        if self.SavePreprocessedImage:
            self.display(pagenum)

        return words

    def imagepreprocessing(self,pagenum):

        # preprocessing
        try:
            inputimg = cv.imread(os.path.join(self.PAGE_DIR,"page"+str(pagenum)+".jpg"))
            self.img = inputimg.copy()
            self.grayimg = cv.cvtColor(self.img,cv.COLOR_BGR2GRAY)
            self.binaryimg = cv.threshold(self.grayimg,200,255,cv.THRESH_BINARY_INV )[1]
            return True
        except:
            return False
    
    # geneate boxes in ascending order of area
    def generate_boxes(self):

        # get the boxes
        dict_of_boxes = pytesseract.image_to_data(self.img,output_type=Output.DICT)  # contain dictionary
        n_boxes = len(dict_of_boxes['level'])

        list_of_boxes = []  # list having boxes in form (w*h,x,y,w,h)
        for i in range(n_boxes):
            list_of_boxes.append([dict_of_boxes['width'][i]*dict_of_boxes['height'][i],dict_of_boxes['left'][i],dict_of_boxes['top'][i],dict_of_boxes['width'][i],dict_of_boxes['height'][i]])
        
        # sort the boxes in term of area
        list_of_boxes = np.array(list_of_boxes)
        bboxes = list_of_boxes[np.argsort(list_of_boxes[:,0])] 
        return bboxes[:,1:]


    def filter(self,bboxes):
        
        # separate horizontal lines, vertical lines, bboxes 
        horizontal_lines,vertical_lines,bboxes = self.remove_lines(bboxes)

        bboxes = self.remove_superboxes(bboxes) # remove boxes which overlap other boxes (remove two big boxes)
        bboxes = self.remove_smaller_intersecting_boxes(bboxes)  # remove smaller box if two intersect (remove small uncessary boxes)
        bboxes = self.correct_boxes(bboxes) # correct each boxes by check the pixel value each its corner and expanding it until find a gap of more than self.GAP
        bboxes = self.refilter(bboxes,0.5) # refilter the boxes remove smaller boxes which overlap more than 50% with other bigger boxes


        horizontal_lines = self.filter_horizontal_line(horizontal_lines) # filter horizontal lines
        vertical_lines = self.filter_vertical_line(vertical_lines) # filter vertical lines
        
        return horizontal_lines,vertical_lines,bboxes
    
    def remove_lines(self,bboxes):

        # lines will have a certain ratio of height/width or width/height which can be used to separate lines and boxes
        horlines = []
        verlines = []
        boxes    = []
        ratio = 0

        for box in bboxes:
            x,y,w,h  = box
            ratio += max(w/h,h/w)
        ratio = ratio/len(bboxes)
        MIN_LINE_RATIO = np.ceil(ratio)
        
        for box in bboxes:
            x,y,w,h = box

            if (w > h and w/h > MIN_LINE_RATIO):
                horlines.append(box)
            elif ( h >= w and h/w > MIN_LINE_RATIO):
                verlines.append(box)
            else:
                boxes.append(box)

        return np.array(horlines),np.array(verlines),np.array(boxes)
    
    def remove_superboxes(self,bboxes):

        # check the intersection, if overlap more than OVERLAP_RATIO , remove the bigger one
        boxes = []

        for j in range(len(bboxes)-1,-1,-1):
            box = bboxes[j]
            for i in range(j):
                com_box = bboxes[i]

                intersect_box = self.intersection(box,com_box)
                if (intersect_box[2]*intersect_box[3] > self.OVERLAP_RATIO *com_box[2]*com_box[3]):
                    break
            else:
                boxes.append(bboxes[j])
        
        return np.array(boxes[::-1])
    
    def remove_smaller_intersecting_boxes(self,bboxes):
        
        # check the intersection, if it NULL, continue, else remove the smaller one
        boxes = []
        NULL_BOX = [0,0,0,0]

        for i in range(len(bboxes)):
            box = bboxes[i]
            for j in range(i+1,len(bboxes)):
                com_box = bboxes[j]

                if np.any(self.intersection(box,com_box) != NULL_BOX):
                    break

            else:
                boxes.append(bboxes[i])
        return np.array(boxes)
    
    def filter_horizontal_line(self,horizontal_lines):
        # check do every detected horizontal line have a continous set of pixels for being a line.
        lines = []
        for line in horizontal_lines:
            x,y,w,h = line

            for yc in range(y,y+h+1):
                count = 0
                xc = x
                while(xc < x+w+1):

                    if (self.binaryimg[yc,xc]):
                        while(self.binaryimg[yc,xc]):
                            xc += 1
                        count += 1

                    else:
                        xc+=1
                if count == 1:
                    lines.append(line)
                    break
        return np.array(lines)
    
    def filter_vertical_line(self,vertical_lines):
        # check do every detected vertical line have a continous set of pixels for being a line.
        lines = []
        for line in vertical_lines:
            x,y,w,h = line

            for xc in range(x,x+w+1):
                count = 0
                yc = y
                while(yc < y+h+1):

                    if (self.binaryimg[yc,xc]):
                        while(self.binaryimg[yc,xc]):
                            yc += 1
                        count += 1

                    else:
                        yc+=1
                if count == 1:
                    lines.append(line)
                    break
        
        return np.array(lines)

    def refilter(self,bboxes,allowence):
        # if two images overlap with more than allowence, take the bigger one (chance of getting right word increase)
        boxes = []
        for i in range(len(bboxes)):
            box = bboxes[i]
            for j in range(i+1,len(bboxes)):
                com_box = bboxes[j]
                intersect_box = self.intersection(box,com_box)
                if (intersect_box[2]*intersect_box[3] > allowence*com_box[2]*com_box[3]):
                    break
            else:
                boxes.append(box)
        
        return np.array(boxes)
    
    def get_word_arr(self):
        # crop every box and retrun list of img,box
        words = []
        
        for box in self.bboxes:
            x,y,w,h = box
            word = self.img[y:y+h+1,x:x+w+1]
            words.append([word,box])
            
        return words



    def intersection(self,box1,box2):

        # return intersection of two boxes
        x = max(box1[0],box2[0])
        y = max(box1[1],box2[1])

        w = min(box1[0]+box1[2],box2[0] + box2[2]) - x
        h = min(box1[1]+box1[3],box2[1] + box2[3]) - y

        if (w < 0) or  (h<0) :
            return [0,0,0,0]
        return np.array([x,y,w,h])


    def union(self,box1,box2):

        # return union of two boxes

        x = min(box1[0],box2[0])
        y = min(box1[1],box2[1])

        w = max(box1[0]+box1[2],box2[0] + box2[2])
        h = max(box1[1]+box1[3],box2[1] + box2[3])

        return np.array([x,y,w,h])
    
    def correct_boxes(self,bboxes):

        # move around corner of each boxes until a gap(SELF.GAP) of inactive pixels are observed in binaryimage in every direction
        pageheight,pagewidth = self.img.shape[:2]
        boxes = []
        GAP = 4
        for idx,box in enumerate(bboxes):

            x,y,w,h = box
            
            gap = GAP
            while(True):
                for xc in range(x,x+w+1):
                    if xc < pagewidth and y>0 and y+h-1<pageheight and self.binaryimg[y-1][xc]:
                        gap=GAP
                        break
                else:
                    gap -= 1
                    if gap < 0:
                        break
                y = y-1
                h = h+1

            
            gap = GAP
            while(True):
                for xc in range(x,x+w+1):
                    if xc < pagewidth and y+h-1 < pageheight and  self.binaryimg[y+h+1][xc]:
                        gap=GAP
                        break
                else:
                    gap -= 1
                    if gap < 0:
                        break
                h = h+1
            gap = GAP
            while(True):
                for yc in range(y,y+h+1):
                    if yc < pageheight and x>0 and x+w-1 <pagewidth and self.binaryimg[yc][x-1]:
                        gap=GAP
                        break
                else:
                    gap -= 1
                    if gap < 0:
                        break
                x = x-1
                w = w+1
            
            gap = GAP
            while(True):
                for yc in range(y,y+h+1):
                    if yc < pageheight and x+w-1 <pagewidth and self.binaryimg[yc][x+w+1]:
                        gap=GAP
                        break
                else:
                    gap -= 1
                    if gap < 0:
                        break
                w = w+1
            
            boxes.append([x,y,w,h])

        return np.array(boxes)

    def save(self,words):
        # Save word image in SELF.WORD_DIR
        
        if not os.path.exists(self.WORD_DIR):
            os.mkdir(self.WORD_DIR)
        for word in words:
            cv.imwrite(os.path.join(self.WORD_DIR,"word"+str(self.WordCount)+".jpg"),word[0])
            self.WordCount += 1
        
    def display(self,pagenum):

        # display the preprocessed image in the SELF.PREPROCESSED_DIR
        img = self.img.copy()
        for box in self.bboxes:
            
            x, y, w, h = box
            
            cv.rectangle(img, (x, y), (x + w, y + h), (0,0,255), 1)

        for box in self.horizontal_lines:
            
            x, y, w, h = box
            
            cv.rectangle(img, (x, y), (x + w, y + h), (0,255,0), 1)
        
        for box in self.vertical_lines:
            
            x, y, w, h = box
            
            cv.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
        
        if not os.path.exists(self.PREPROCESSED_DIR):
            os.mkdir(self.PREPROCESSED_DIR)
        cv.imwrite(os.path.join(self.PREPROCESSED_DIR,"page"+str(pagenum)+".jpg"),img)


