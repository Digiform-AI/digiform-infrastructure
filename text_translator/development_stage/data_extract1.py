# from flask import Flask

from PIL import Image
import pytesseract
import json
import math
# to browse for a file on your computer or mobile device using the built-in tkinter library
# tkinter is a GUI library, so this program requires a graphical user interface to be present
import tkinter as tk
from tkinter import filedialog
import os


import fitz

import cv2
from pdf2image import convert_from_path
import platform






def textFromCoordinates(a, b, c, d):
    x = round((a/72) * 200)
    h = round(abs(((b / 72)*200) - ((d / 72) * 200)))
    y = round(((842 - b) / 72) * 200) - h
    w = round(abs(((a / 72)*200) - ((c / 72) * 200)))

    ROI = thresh[y:y+h,x:x+w]
    if(platform.system() == "Windows"):
        data = pytesseract.image_to_string(ROI, lang='eng',config='--psm 6')
    if data in ("eo", "e", "C"):
        data = "Yes\n"
    elif data in ("", "pS"):
        data = "No\n"

    print(data)
    text_list.append(data)


root = tk.Tk()
root.withdraw()


print("Please choose the file")

file_path = filedialog.askopenfilename()
file_name = os.path.basename(file_path)
print("Selected file name:", file_name)

text_list = []


# Folder where tesseract is installed
# This is required only for Windows machine 
# Please comment this line if you run on different machine
if(platform.system() == "Windows"):
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = Image.open(file_path)
width = image.width
height = image.height
dpi = image.info['dpi']
# print(dpi)

if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
    
    
    '''
    # The selected file is an image, so load it as a PIL image object
    pages = [Image.open(file_path)]

    # Loop through each page and perform OCR
    for page in pages:
        # Perform OCR on the page
        text = pytesseract.image_to_string(page)
        # Append extracted text to the list     

        text_list.append(text)

        '''
    




    image = cv2.imread(file_path, 0)
    thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    textFromCoordinates(181.07736199999999, 716.11724900000002, 369.879547, 746.70416299999999)
    textFromCoordinates(181.45524599999999, 672.79022199999997, 209.256439, 700.59143099999994)
    textFromCoordinates(180.961365, 610.03417999999999, 369.87951700000002, 641.34619099999998)
    textFromCoordinates(180.37136799999999, 536.44274900000005, 369.87933299999997, 565.52160600000002)
    textFromCoordinates(218.71044900000001, 459.85290500000002, 248.00308200000001, 487.52307100000002)
    textFromCoordinates(73.834304799999998, 396.49487299999998, 94.930130000000005, 416.66924999999998)
    textFromCoordinates(73.834304799999998, 365.20684799999998, 94.930130000000005, 385.38122600000003)
    textFromCoordinates(73.834304799999998, 333.33880599999998, 94.930130000000005, 353.51318400000002)
    textFromCoordinates(75.042625400000006, 261.55731200000002, 93.721824600000005, 280.23651100000001)
    textFromCoordinates(75.042625400000006, 232.74130199999999, 93.721824600000005, 251.420502)
    textFromCoordinates(75.042625400000006, 206.53208900000001, 93.721824600000005, 225.211288)
    textFromCoordinates(76.251640300000005, 174.702606, 94.930839500000005, 193.38180500000001)


    '''
    # x,y,w,h = 37, 625, 309, 28  

    # x,y,w,h = 181, 716, 369, 746


    a,b,c,d = 181.07736199999999, 716.11724900000002, 369.879547, 746.70416299999999

    # a,b,c,d = 181.45524599999999, 672.79022199999997, 209.256439, 700.59143099999994
    # a,b,c,d =  180.961365, 610.03417999999999, 369.87951700000002, 641.34619099999998

    # x = math.ceil((a/612)*width)    
    # y = math.ceil((1-(b/792))*height)
    # w = math.ceil(((c-a)/595) * width)
    # h = math.ceil(((d-b) / 595) * height)

    x = round((a/72) * 200)
    h = round(abs(((b / 72)*200) - ((d / 72) * 200)))
    y = round(((842 - b) / 72) * 200) - h
    w = round(abs(((a / 72)*200) - ((c / 72) * 200)))
    


    # w = round((c/72) * 200)
    # h = round(((842 - d) / 72) * 200)


    # print(x,y,w,h)
    # x,y,w,h = x, y-h, w, h

    # x,y,w,h = 362, 275, 369, 57                   
    # x,y,w,h = 181.07736199999999, 716.11724900000002, 369.879547, 746.70416299999999
    
    
    
    # x,y,w,h = 200, 716, 500, 746
    # x,y,w,h = 200, 116, 500, 746
    
    # x,y,w,h = 1000, 5900, 1088, 1008

    ROI = thresh[y:y+h,x:x+w]
    data = pytesseract.image_to_string(ROI, lang='eng',config='--psm 6')
    print(data)

    # cv2.imshow('thresh', thresh)
    cv2.imshow('ROI', ROI)
    cv2.waitKey()

    '''




elif file_name.lower().endswith(('.pdf')):
    '''
    
    # txt = []
    doc = fitz.open(file_path)            # some existing PDF
    for page in doc:
        text = page.get_text("text")
        text = text.split('\n')
        text_list.extend(text)
 
        '''
    


    print("Before command converting to image\n")
    poppler_path = r'C:\Program Files (x86)\poppler-23.01.0\Library\bin'

    pdftoimagefile = convert_from_path(poppler_path,file_path)
    print("Before converting to image\n")
    pdftoimagefile.save(file_name+'.jpg', 'JPEG')

    print("After converting to image\n")




    image = cv2.imread((file_name+'.jpg'), 0)
    thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # x,y,w,h = 37, 625, 309, 28  

    x,y,w,h = 181.07736199999999, 716.11724900000002, 369.879547, 746.70416299999999
    ROI = thresh[y:y+h,x:x+w]
    data = pytesseract.image_to_string(ROI, lang='eng',config='--psm 6')
    print(data)




# Convert to JSON
data = {'text': text_list}
json_data = json.dumps(data,indent=4)
# print(json_data)


# Write the JSON data to a file
with open('file_output.json', 'w') as f:
    f.write(json_data)