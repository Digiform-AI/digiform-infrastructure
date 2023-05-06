from PIL import Image
from pdf2image import convert_from_path
import pytesseract
import json
import io

# to browse for a file on your computer or mobile device using the built-in tkinter library
# tkinter is a GUI library, so this program requires a graphical user interface to be present
import tkinter as tk
from tkinter import filedialog
import os



# def performOCR(image):
#     # Perform OCR
#     text = pytesseract.image_to_string(image)
#     text_list.append(text)




root = tk.Tk()
root.withdraw()



print("Hello")

file_path = filedialog.askopenfilename()
file_name = os.path.basename(file_path)
print("Selected file name:", file_name)


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'



# if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
#     # Load image or pdf
#     image = Image.open(file_path)

#     text = pytesseract.image_to_string(image)
#     data = {'text': text}
#     # performOCR(image)

# # or
# elif file_name.lower().endswith(('.pdf')):
#     pages = convert_from_path(file_name)
#     # image = pages[0]


#     for page in pages:
#         # image = page
#         # performOCR(image)


#         # Perform OCR
#         text = pytesseract.image_to_string(page)
#         text_list.append(text)

#     data = {'text': text_list}


# print("fine")

# # Convert to JSON
# # data = {'text': text_list}
# json_data = json.dumps(data)

# print(json_data)





if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
    # The selected file is an image, so load it as a PIL image object
    pages = [Image.open(file_path)]

elif file_name.lower().endswith(('.pdf')):
    pages = convert_from_path(file_path)


# Loop through each page and perform OCR
text_list = []
for page in pages:
    # Perform OCR on the page
    text = pytesseract.image_to_string(page)
    # Append extracted text to the list
    text_list.append(text+"\n\n")

# Convert to JSON
data = {'text': text_list}
json_data = json.dumps(data,indent=4)

#  Write JSON data to file
# with io.open('output.json', 'w', encoding='utf8') as outfile:
#     outfile.write(json_data)

# print("Data written to output.json file.")


# print(json_data)





# Write the JSON data to a file
with open('output.json', 'w') as f:
    f.write(json_data)