'''import cv2
import pytesseract

pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'  # your path may be different


image = cv2.imread('form.jpg')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
contours = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]

with open("image_to_text.txt", "w") as f:
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        roi = opening[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi, config='--psm 11')
        # print('Detected text:', text)

        print(text, file=f)

'''











import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = 'C:\Program Files\Tesseract-OCR\\tesseract.exe'  # your path may be different

# Load the image
img = cv2.imread('sample1.pdf')

# Preprocess the image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

# Perform text detection using Tesseract OCR
text = pytesseract.image_to_string(gray, lang='eng', config='--psm 6')

# Print the detected text
print(text)
