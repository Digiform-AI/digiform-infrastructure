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

import re

import numpy as np


from flask import Flask, jsonify, request
import json
import requests


def crop_img(img, scale=1.0):
    center_x, center_y = img.shape[1] / 2, img.shape[0] / 2
    width_scaled, height_scaled = img.shape[1] * scale, img.shape[0] * scale
    left_x, right_x = center_x - width_scaled / 2, center_x + width_scaled / 2
    top_y, bottom_y = center_y - height_scaled / 2, center_y + height_scaled / 2
    img_cropped = img[int(top_y):int(bottom_y), int(left_x):int(right_x)]
    return img_cropped




def textFromCoordinates(a, b, c, d, height, checkbox):
    x = round((a/72) * 200)
    h = round(abs(((b / 72)*200) - ((d / 72) * 200)))
    y = round(((height - b) / 72) * 200) - h
    w = round(abs(((a / 72)*200) - ((c / 72) * 200)))

    # print(x,h,y,w)
    ROI = thresh[y:y+h,x:x+w]
    
    # temporary for testing without api
    checkbox = (abs(h/w) > 0.9 and abs(h/w) < 1.1)

    
    if checkbox:
        img_cropped = crop_img(ROI, CROP)            # Crop to remove any border
    
        n_black_pix = np.sum(img_cropped < PIX_RANGE)
    
        if n_black_pix > THRESHOLD:
            text_list.append("Yes\n")
        else:
            text_list.append("No\n")
    else:
        if(platform.system() == "Windows"):
            data = pytesseract.image_to_string(ROI, lang='eng', config='--psm 6')
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


THRESHOLD = 100 # Threshhold for stray marks, in pixels
CROP = 0.85 # Percentage of image to scan
PIX_RANGE = 100 # Pixel darkness to consider marked



'''
# Sample extracting data from covid19india
response_API = requests.get('https://api.covid19india.org/state_district_wise.json')
#print(response_API.status_code)
data = response_API.text
parse_json = json.loads(data)
active_case = parse_json['Andaman and Nicobar Islands']['districtData']['South Andaman']['active']
print("Active cases in South Andaman:", active_case)

'''







points = [181.07736199999999, 716.11724900000002, 369.879547, 746.70416299999999, 181.45524599999999, 672.79022199999997, 209.256439, 700.59143099999994, 180.961365, 610.03417999999999, 369.87951700000002, 641.34619099999998, 180.37136799999999, 536.44274900000005, 369.87933299999997, 565.52160600000002, 218.71044900000001, 459.85290500000002, 248.00308200000001, 487.52307100000002, 73.834304799999998, 396.49487299999998, 94.930130000000005, 416.66924999999998, 73.834304799999998, 365.20684799999998, 94.930130000000005, 385.38122600000003, 73.834304799999998, 333.33880599999998, 94.930130000000005, 353.51318400000002, 75.042625400000006, 261.55731200000002, 93.721824600000005, 280.23651100000001, 75.042625400000006, 232.74130199999999, 93.721824600000005, 251.420502, 75.042625400000006, 206.53208900000001, 93.721824600000005, 225.211288, 76.251640300000005, 174.702606, 94.930839500000005, 193.38180500000001]
if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
    image = cv2.imread(file_path, 0)
    thresh = 255 - cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    


    # final code once hooked up to api
    # for field in fields:
    #     textFromCoordinates(field.rect[0], field.rect[1], field.rect[2], field.rect[3], field.pageHeight, field.type == "checkbox")
    for i in range(0, len(points), 4):
        textFromCoordinates(points[i], points[i+1], points[i+2], points[i+3], 842 , True)


# Convert to JSON
data = {'text': text_list}
json_data = json.dumps(data,indent=4)
# print(json_data)


# Write the JSON data to a file
with open('file_output.json', 'w') as f:
    f.write(json_data)
    
print('Text extraction complete!')