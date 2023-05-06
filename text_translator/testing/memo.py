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
    # cv2.imshow('thresh', thresh)
    cv2.imshow('ROI', ROI)
    cv2.waitKey()

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


image = cv2.imread(file_path, 0)
thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]


x,y,w,h = 80, 316, 3900, 46   # Name and Roll No

# textFromCoordinates(181, 716, 369, 746)
textFromCoordinates(x,y,w,h)


x,y,w,h = 80, 16, 3900, 46
textFromCoordinates(x,y,w,h)


# x,y,w,h = 181, 716, 369, 746
# ROI = thresh[y:y+h,x:x+w]
# data = pytesseract.image_to_string(ROI, lang='eng',config='--psm 6')
# print(data)

# # cv2.imshow('thresh', thresh)
# cv2.imshow('ROI', ROI)
# cv2.waitKey()



# Convert to JSON
data = {'text': text_list}
json_data = json.dumps(data,indent=4)
# print(json_data)


# Write the JSON data to a file
with open('memo_data.json', 'w') as f:
    f.write(json_data)