from PIL import Image
from pytesseract import pytesseract

import PyPDF2



# Defining paths to tesseract.exe
# and the image we would be using
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


image_path = r"form.jpg"

# Opening the image & storing it in an image object
img = Image.open(image_path)

# Providing the tesseract executable
# location to pytesseract library
pytesseract.tesseract_cmd = path_to_tesseract

# Passing the image object to image_to_string() function
# This function will extract the text from the image
text = pytesseract.image_to_string(img)

# Displaying the extracted text
# print(text[:-1])
with open("output.txt", "w") as f:
  print(text[:-1], file=f)












# pdf_file = open('sample application.pdf', 'rb')
pdf_file = open('Bhashampally.pdf', 'rb')
pdf_reader = PyPDF2.PdfReader(pdf_file)

with open('pdf_output.txt', 'w', encoding='utf8') as text_file:
    # text_file = open('pdf_output.txt', 'w')
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text = page.extract_text()        
        text_file.write(text+"\n\n\n\n\n\n\n")
pdf_file.close()
text_file.close()
