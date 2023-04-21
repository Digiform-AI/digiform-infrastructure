import numpy as np
import cv2, os
import pytesseract
from pytesseract import Output
from PIL import Image

# API example that does not require any actual api call or field data. Simply a scaffold to show the process of 
# iterating many files 
debug = False
simple_debug = True
input_folder = 'crop-pages'

# NOTE: the input directory must contain one file for each page of the multi-page # document (1 image only if 1 page document). This is for multi-page conversion support.
# NOTE: if the api is called with fields that belong on x pages, the code will error if there are
# not the expected x pages in the documents folder.

class extraction:

    dpi = 200
    
    # cuts out the border of the checkbox so it does not interfere with our check detection
    def zoom_img(img, scale=1.0):
        center_x, center_y = img.shape[1] / 2, img.shape[0] / 2
        width_scaled, height_scaled = img.shape[1] * scale, img.shape[0] * scale
        left_x, right_x = center_x - width_scaled / 2, center_x + width_scaled / 2
        top_y, bottom_y = center_y - height_scaled / 2, center_y + height_scaled / 2
        img_cropped = img[int(top_y):int(bottom_y), int(left_x):int(right_x)]
        return img_cropped


    # Determines whether this image file is checked as yes
    def isChecked(ROI):
        
        THRESHOLD = 20 # Threshhold for stray marks, in pixels
        CROP = 0.6 # Percentage of image to scan
        PIX_RANGE = 100 # Pixel darkness to consider marked

        img_cropped = extraction.zoom_img(ROI, CROP)            # Crop to remove any border
        n_black_pix = np.sum(img_cropped < PIX_RANGE)

        if debug:
            ''' debug the checkboxes to test the tolerance variables'''
            cv2.imshow('box', ROI)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            print(n_black_pix, THRESHOLD)

        if n_black_pix > THRESHOLD:
            return True
        return False

    def crop(path, width, height):
        # Load the image and set the dpi
        im = Image.open(path)

        # Set the DPI
        im.info['dpi'] = (extraction.dpi, extraction.dpi)

        # Save the image with the new DPI
        im.save(path)


        '''Load the image with the new dpi into opencv'''
        img = cv2.imread(path)

        if debug:
            cv2.imshow('Original Image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if debug:
            cv2.imshow('Grayscale Image', gray)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Apply adaptive thresholding to convert the image to a binary image
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 71, 25)

        if debug:
            cv2.imshow('Binary threshold Image', thresh)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        # Find contours in the binary image
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize the maximum area and corresponding contour
        max_area = 0
        max_cnt = None

        # Loop through each contour
        for cnt in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(cnt)

            # If the area is small, ignore the contour
            if area < 100:
                continue

            # Check if the contour is closed
            perimeter = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.04 * perimeter, True)
            if len(approx) != 4:
                continue

            # Check if the area of the contour is the maximum so far
            if area > max_area:
                max_area = area
                max_cnt = approx

        # Extend the corners of the contour to align them along the horizontal and vertical axes
        max_cnt[0][0][1] -= 1 # Top corner
        max_cnt[1][0][0] += .01 # Right corner
        max_cnt[2][0][1] += 1 # Bottom corner
        max_cnt[3][0][0] -= 1 # Left corner

        a = max_cnt[0][0]
        b = max_cnt[1][0]
        c = max_cnt[2][0]
        d = max_cnt[3][0]

        # Create a white mask of the same size as the input image
        mask = np.ones(img.shape[:2], dtype=np.uint8) * 255

        # Fill the mask with black inside the detected boundary
        cv2.drawContours(mask, [max_cnt], 0, 0, -1)

        # Copy the original image content inside the detected boundary onto the new image
        new_img = np.copy(img)
        new_img[np.where(mask==0)] = img[np.where(mask==0)]

        

        # Fill the area outside the detected boundary with white color
        new_img[np.where(mask==255)] = [255, 255, 255]

        if debug:
            cv2.imshow('Content in boundary', new_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        '''Fix the warping of the image '''
        
        # if bl/tl are swapped, fix them to resolve rotation errors
        if (b[1] > new_img.shape[1] / 2): # we need to swap BL and TL coords
            if debug:
                print('bad rotation! fixing...', b[1], new_img.shape[1] / 2)
            temp = b # save a so we dont loose it 
    
            b = c
            c = d
            d = a
            a = temp
            

        src = np.array([[b[0], b[1]], [a[0], a[1]],[d[0], d[1]],[c[0], c[1]]])
        dest = np.array([[0,0],[width,0],[width,height],[0,height]])

        # Calculate the transformation matrix
        M, _ = cv2.findHomography(src, dest)

        # Apply perspective correction to the image
        img_corrected = cv2.warpPerspective(new_img, M, (round(width), round(height)))

        ''' Make sure the image is the right 90 degree orientation'''
        gray = cv2.cvtColor(img_corrected, cv2.COLOR_BGR2GRAY)
        # Perform OCR on the image and get the OSD information
        osd = pytesseract.image_to_osd(gray, output_type=Output.DICT)

        # Extract the rotation angle from the OSD information
        angle = int(osd['orientation'])

        #Check if the image is rotated
        if debug:
            if angle == 0:
                print('The image is straight.')
            else:
                print(f'The image is rotated {angle} degrees.')

        # Rotate the image to the correct orientation
        if angle > 250 and angle < 290:
            img_corrected = cv2.rotate(img_corrected, cv2.ROTATE_90_CLOCKWISE)
        elif angle > 160 and angle < 200:
            img_corrected = cv2.rotate(img_corrected, cv2.ROTATE_180)
        elif angle > 70 and angle < 110:
            img_corrected = cv2.rotate(img_corrected, cv2.ROTATE_90_COUNTERCLOCKWISE)

        img_corrected = cv2.resize(img_corrected, (round(width), round(height)))

        ''' Show the results '''
        if debug:
            cv2.imshow('Corrected Image', img_corrected)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        return img_corrected


    lines = [
        {
            "Line": "Home Inspection",
            "WordsArray": [
                {
                    "Conf": 99.98,
                    "Loc": [
                        0.3644,
                        0.0223,
                        0.4529,
                        0.0409
                    ],
                    "Word": "Home"
                },
                {
                    "Conf": 99.68,
                    "Loc": [
                        0.4629,
                        0.0212,
                        0.6173,
                        0.0446
                    ],
                    "Word": "Inspection"
                }
            ]
        },
        {
            "Line": "T",
            "WordsArray": [
                {
                    "Conf": 97.6,
                    "Loc": [
                        0.8904,
                        0.0488,
                        0.9795,
                        0.0877
                    ],
                    "Word": "T"
                }
            ]
        },
        {
            "Line": "Property Address:",
            "WordsArray": [
                {
                    "Conf": 99.98,
                    "Loc": [
                        0.0352,
                        0.0902,
                        0.1357,
                        0.1095
                    ],
                    "Word": "Property"
                },
                {
                    "Conf": 99.97,
                    "Loc": [
                        0.1415,
                        0.0916,
                        0.2443,
                        0.1071
                    ],
                    "Word": "Address:"
                }
            ]
        },
        {
            "Line": "11 Hay Ln",
            "WordsArray": [
                {
                    "Conf": 95.77,
                    "Loc": [
                        0.2622,
                        0.0932,
                        0.2868,
                        0.1145
                    ],
                    "Word": "11"
                },
                {
                    "Conf": 99.85,
                    "Loc": [
                        0.325,
                        0.0944,
                        0.4002,
                        0.1225
                    ],
                    "Word": "Hay"
                },
                {
                    "Conf": 99.88,
                    "Loc": [
                        0.4418,
                        0.0938,
                        0.4848,
                        0.1122
                    ],
                    "Word": "Ln"
                }
            ]
        },
        {
            "Line": "Inspection Date:",
            "WordsArray": [
                {
                    "Conf": 99.7,
                    "Loc": [
                        0.0366,
                        0.1221,
                        0.1587,
                        0.1405
                    ],
                    "Word": "Inspection"
                },
                {
                    "Conf": 99.91,
                    "Loc": [
                        0.1665,
                        0.1232,
                        0.2293,
                        0.1384
                    ],
                    "Word": "Date:"
                }
            ]
        },
        {
            "Line": "12/18/2022",
            "WordsArray": [
                {
                    "Conf": 99.38,
                    "Loc": [
                        0.2685,
                        0.1197,
                        0.4989,
                        0.1465
                    ],
                    "Word": "12/18/2022"
                }
            ]
        },
        {
            "Line": "Inspector:",
            "WordsArray": [
                {
                    "Conf": 97.85,
                    "Loc": [
                        0.0363,
                        0.1544,
                        0.153,
                        0.1726
                    ],
                    "Word": "Inspector:"
                }
            ]
        },
        {
            "Line": "Mike Hamilton",
            "WordsArray": [
                {
                    "Conf": 99.29,
                    "Loc": [
                        0.2664,
                        0.1553,
                        0.3696,
                        0.1773
                    ],
                    "Word": "Mike"
                },
                {
                    "Conf": 99.95,
                    "Loc": [
                        0.4027,
                        0.1539,
                        0.5793,
                        0.1769
                    ],
                    "Word": "Hamilton"
                }
            ]
        },
        {
            "Line": "Client Details",
            "WordsArray": [
                {
                    "Conf": 99.89,
                    "Loc": [
                        0.0385,
                        0.206,
                        0.1254,
                        0.2248
                    ],
                    "Word": "Client"
                },
                {
                    "Conf": 99.97,
                    "Loc": [
                        0.1358,
                        0.2064,
                        0.2391,
                        0.225
                    ],
                    "Word": "Details"
                }
            ]
        },
        {
            "Line": "Name:",
            "WordsArray": [
                {
                    "Conf": 99.94,
                    "Loc": [
                        0.0378,
                        0.2424,
                        0.1143,
                        0.2572
                    ],
                    "Word": "Name:"
                }
            ]
        },
        {
            "Line": "Carlos Amana",
            "WordsArray": [
                {
                    "Conf": 90.55,
                    "Loc": [
                        0.1616,
                        0.2409,
                        0.2876,
                        0.2611
                    ],
                    "Word": "Carlos"
                },
                {
                    "Conf": 99.94,
                    "Loc": [
                        0.3214,
                        0.2418,
                        0.442,
                        0.2603
                    ],
                    "Word": "Amana"
                }
            ]
        },
        {
            "Line": "Phone:",
            "WordsArray": [
                {
                    "Conf": 99.9,
                    "Loc": [
                        0.5858,
                        0.239,
                        0.6665,
                        0.2542
                    ],
                    "Word": "Phone:"
                }
            ]
        },
        {
            "Line": "555-294-3398",
            "WordsArray": [
                {
                    "Conf": 94.13,
                    "Loc": [
                        0.6767,
                        0.2362,
                        0.9,
                        0.2551
                    ],
                    "Word": "555-294-3398"
                }
            ]
        },
        {
            "Line": "Address:",
            "WordsArray": [
                {
                    "Conf": 99.96,
                    "Loc": [
                        0.0361,
                        0.2679,
                        0.1391,
                        0.2832
                    ],
                    "Word": "Address:"
                }
            ]
        },
        {
            "Line": "1087 Express Drive N",
            "WordsArray": [
                {
                    "Conf": 99.94,
                    "Loc": [
                        0.157,
                        0.2689,
                        0.2277,
                        0.287
                    ],
                    "Word": "1087"
                },
                {
                    "Conf": 99.94,
                    "Loc": [
                        0.2524,
                        0.267,
                        0.3893,
                        0.288
                    ],
                    "Word": "Express"
                },
                {
                    "Conf": 99.96,
                    "Loc": [
                        0.4133,
                        0.2643,
                        0.5029,
                        0.2836
                    ],
                    "Word": "Drive"
                },
                {
                    "Conf": 99.97,
                    "Loc": [
                        0.5294,
                        0.2652,
                        0.5558,
                        0.2819
                    ],
                    "Word": "N"
                }
            ]
        },
        {
            "Line": "Reported Issues",
            "WordsArray": [
                {
                    "Conf": 99.98,
                    "Loc": [
                        0.0399,
                        0.3112,
                        0.1757,
                        0.3335
                    ],
                    "Word": "Reported"
                },
                {
                    "Conf": 99.59,
                    "Loc": [
                        0.1878,
                        0.3118,
                        0.2793,
                        0.3296
                    ],
                    "Word": "Issues"
                }
            ]
        },
        {
            "Line": "Mold",
            "WordsArray": [
                {
                    "Conf": 99.93,
                    "Loc": [
                        0.046,
                        0.3551,
                        0.1022,
                        0.3698
                    ],
                    "Word": "Mold"
                }
            ]
        },
        {
            "Line": "Primary bathroom has black mold",
            "WordsArray": [
                {
                    "Conf": 99.79,
                    "Loc": [
                        0.2192,
                        0.3517,
                        0.3654,
                        0.3799
                    ],
                    "Word": "Primary"
                },
                {
                    "Conf": 99.89,
                    "Loc": [
                        0.3901,
                        0.3504,
                        0.5597,
                        0.3698
                    ],
                    "Word": "bathroom"
                },
                {
                    "Conf": 99.99,
                    "Loc": [
                        0.5793,
                        0.3487,
                        0.6342,
                        0.3659
                    ],
                    "Word": "has"
                },
                {
                    "Conf": 99.57,
                    "Loc": [
                        0.6544,
                        0.3469,
                        0.7413,
                        0.3662
                    ],
                    "Word": "black"
                },
                {
                    "Conf": 99.69,
                    "Loc": [
                        0.7635,
                        0.3489,
                        0.8464,
                        0.3659
                    ],
                    "Word": "mold"
                }
            ]
        },
        {
            "Line": "behind the sink. Requires complete",
            "WordsArray": [
                {
                    "Conf": 99.91,
                    "Loc": [
                        0.2216,
                        0.3762,
                        0.3417,
                        0.3955
                    ],
                    "Word": "behind"
                },
                {
                    "Conf": 100,
                    "Loc": [
                        0.37,
                        0.3772,
                        0.4353,
                        0.3939
                    ],
                    "Word": "the"
                },
                {
                    "Conf": 78.39,
                    "Loc": [
                        0.4589,
                        0.3749,
                        0.5372,
                        0.3933
                    ],
                    "Word": "sink."
                },
                {
                    "Conf": 99.85,
                    "Loc": [
                        0.549,
                        0.3714,
                        0.6865,
                        0.3995
                    ],
                    "Word": "Requires"
                },
                {
                    "Conf": 82.01,
                    "Loc": [
                        0.7184,
                        0.375,
                        0.8691,
                        0.3968
                    ],
                    "Word": "complete"
                }
            ]
        },
        {
            "Line": "remodel",
            "WordsArray": [
                {
                    "Conf": 84.97,
                    "Loc": [
                        0.2217,
                        0.4002,
                        0.3602,
                        0.4153
                    ],
                    "Word": "remodel"
                }
            ]
        },
        {
            "Line": "Framing",
            "WordsArray": [
                {
                    "Conf": 99.81,
                    "Loc": [
                        0.0448,
                        0.4286,
                        0.1392,
                        0.4466
                    ],
                    "Word": "Framing"
                }
            ]
        },
        {
            "Line": "Electrical",
            "WordsArray": [
                {
                    "Conf": 99.79,
                    "Loc": [
                        0.0454,
                        0.5302,
                        0.1525,
                        0.5452
                    ],
                    "Word": "Electrical"
                }
            ]
        },
        {
            "Line": "Wiring is old and ungrounded,",
            "WordsArray": [
                {
                    "Conf": 94.58,
                    "Loc": [
                        0.2177,
                        0.5251,
                        0.3332,
                        0.5566
                    ],
                    "Word": "Wiring"
                },
                {
                    "Conf": 99.99,
                    "Loc": [
                        0.3656,
                        0.5249,
                        0.4007,
                        0.5461
                    ],
                    "Word": "is"
                },
                {
                    "Conf": 99.79,
                    "Loc": [
                        0.4326,
                        0.5263,
                        0.4891,
                        0.5449
                    ],
                    "Word": "old"
                },
                {
                    "Conf": 100,
                    "Loc": [
                        0.5157,
                        0.5215,
                        0.5809,
                        0.5427
                    ],
                    "Word": "and"
                },
                {
                    "Conf": 97.21,
                    "Loc": [
                        0.6065,
                        0.5241,
                        0.8376,
                        0.55
                    ],
                    "Word": "ungrounded,"
                }
            ]
        },
        {
            "Line": "should rewire entire home",
            "WordsArray": [
                {
                    "Conf": 99.26,
                    "Loc": [
                        0.2288,
                        0.5578,
                        0.3484,
                        0.5764
                    ],
                    "Word": "should"
                },
                {
                    "Conf": 99.71,
                    "Loc": [
                        0.3795,
                        0.5531,
                        0.5094,
                        0.5744
                    ],
                    "Word": "rewire"
                },
                {
                    "Conf": 99.97,
                    "Loc": [
                        0.5418,
                        0.5481,
                        0.6653,
                        0.5725
                    ],
                    "Word": "entire"
                },
                {
                    "Conf": 99.96,
                    "Loc": [
                        0.6979,
                        0.5497,
                        0.8,
                        0.5692
                    ],
                    "Word": "home"
                }
            ]
        },
        {
            "Line": "Plumbing",
            "WordsArray": [
                {
                    "Conf": 99.8,
                    "Loc": [
                        0.046,
                        0.6318,
                        0.1561,
                        0.6494
                    ],
                    "Word": "Plumbing"
                }
            ]
        },
        {
            "Line": "Roof",
            "WordsArray": [
                {
                    "Conf": 99.92,
                    "Loc": [
                        0.0474,
                        0.7322,
                        0.101,
                        0.7473
                    ],
                    "Word": "Roof"
                }
            ]
        },
        {
            "Line": "Foundation",
            "WordsArray": [
                {
                    "Conf": 99.96,
                    "Loc": [
                        0.0444,
                        0.8332,
                        0.1747,
                        0.8489
                    ],
                    "Word": "Foundation"
                }
            ]
        },
        {
            "Line": "HVAC",
            "WordsArray": [
                {
                    "Conf": 99.91,
                    "Loc": [
                        0.0435,
                        0.9255,
                        0.1079,
                        0.9401
                    ],
                    "Word": "HVAC"
                }
            ]
        }
    ]

    def is_image_file(path):
        extension = os.path.splitext(path)[1].lower()
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        return extension in image_extensions


    # do not call the function once for each page.
    # call it once for each form, all items in the folder must be pages of the form.
    def fill_fields(fields):
        pageIndex = 0
        ''' Execute for each page '''

        # file path to the image taken of this page
        for filename in os.listdir(input_folder):
            f = os.path.join(input_folder, filename)

        # proceed if it is a file (image)
            if extraction.is_image_file(f):
                path = f

                pageHeight = 0
                pageWidth = 0

                # Gather page-persistent data
                for key in fields.keys():
                    # Find a field on this page to set our data
                    if (fields[key]['pageIndex'] == pageIndex):
                        pageHeight = fields[key]["pageHeight"]
                        pageWidth = fields[key]["pageWidth"]
                        break
                
                ''' LOAD THE PAGE IMAGE AND CROP TO DESIRED SIZE '''
                img = extraction.crop(path, pageWidth, pageHeight)

                # show the output image
                if simple_debug:
                    cv2.imshow("res", img)
                    cv2.waitKey(0)
                    cv2.destroyAllWindows()

                ''' GET THE EXTRACTED DATA (lines)'''



                ''' PREPARING CHECKBOX DETECTION '''
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # first the scanned and cropped page is to become grayscale

                thresh = 255 - cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] # now we can binary it

                # iterate over each field in the document
                for key in fields.keys():

                    # procede only if this field is on the current page
                    if fields[key]['pageIndex'] == pageIndex:

                        # store important data for calculations of this field
                        rect = fields[key]["rect"]
                        is_text = (fields[key]["type"] == "text")

                        # begin managing the fields. If text, find extracted data. If checkbox, analyze the response for it
                        x1 = ((rect[0] / 72) * extraction.dpi) / pageWidth
                        h = ((abs(((rect[1] / 72) * extraction.dpi) - ((rect[3] / 72) * extraction.dpi)))) / pageHeight
                        y2 = ((((pageHeight - rect[1]) / 72) * extraction.dpi) - h) / pageHeight
                        x2 = ((rect[2] / 72) * extraction.dpi) / pageWidth
                        y1 = y2 - h

                        
                        if is_text:
                            # set a tolerance threshold for text searching, then all coordinates
                            t = ((2.5 / 72) * extraction.dpi ) / pageHeight 

                            result = ''
                            for line in extraction.lines:
                                for word in line["WordsArray"]:
                                    loc = word["Loc"]

                                    if (x1 - t <= loc[0] and loc[0] <= x2 + t and y1 - t <= loc[1] and loc[1] <= y2 + t):
                                        result += word["Word"]+' '

                        else: # checkbox
                            #print(y1,y2,x1,x2)
                            ROI = thresh[round(y1 * pageHeight):round(y2 * pageHeight), round(x1 * pageWidth):round(x2 * pageWidth)] # set our region of interest to the checkbox
                            result = 'Yes' if extraction.isChecked(ROI) else 'No'

                        # Set the result that we extracted from the page back into the json
                        fields[key]["value"] = result
                        if debug:
                            #print(result)
                            pass
                pageIndex += 1
        # Each file has been processed, fields is completely filled in
        #return fields


fields = {
        "0": {
        "choiceName": "",
        "groupName": "",
        "index": 0,
        "name": "Address",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            148.227661,
            746.384216,
            537.304138,
            767.435242
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "1": {
        "choiceName": "",
        "groupName": "",
        "index": 1,
        "name": "Date",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            148.227661,
            720.072327,
            537.304138,
            741.123352
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "2": {
        "choiceName": "",
        "groupName": "",
        "index": 2,
        "name": "Inspector",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            148.227661,
            693.373718,
            537.304138,
            714.424744
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "3": {
        "choiceName": "",
        "groupName": "",
        "index": 3,
        "name": "Client Name",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            85.8391037,
            623.338623,
            342.690369,
            642.601379
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "4": {
        "choiceName": "",
        "groupName": "",
        "index": 4,
        "name": "Client Address",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            85.8963165,
            600.965454,
            537.285828,
            620.22821
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "5": {
        "choiceName": "",
        "groupName": "",
        "index": 5,
        "name": "Client Phone",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            400.13269,
            623.338501,
            537.378235,
            642.399536
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "6": {
        "choiceName": "",
        "groupName": "",
        "index": 6,
        "name": "Mold Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            493.197998,
            55.2906494,
            519.726807
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "7": {
        "choiceName": "",
        "groupName": "",
        "index": 7,
        "name": "Framing Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            27.2672195,
            423.598389,
            56.2514801,
            450.127197
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "8": {
        "choiceName": "",
        "groupName": "",
        "index": 8,
        "name": "Electrical Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            345.862488,
            55.2906456,
            372.391296
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "9": {
        "choiceName": "",
        "groupName": "",
        "index": 9,
        "name": "Plumbing Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            262.183777,
            55.2906456,
            288.712585
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "10": {
        "choiceName": "",
        "groupName": "",
        "index": 10,
        "name": "Roof Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            177.273422,
            55.2906456,
            203.802231
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "11": {
        "choiceName": "",
        "groupName": "",
        "index": 11,
        "name": "Foundation Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            92.0914307,
            55.2906456,
            118.620239
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "12": {
        "choiceName": "",
        "groupName": "",
        "index": 12,
        "name": "HVAC Issues?",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            26.3063908,
            10.6557293,
            55.2906456,
            37.1845398
        ],
        "singleSelectionOnly": False,
        "type": "checkbox",
        "value": "No"
        },
        "13": {
        "choiceName": "",
        "groupName": "",
        "index": 13,
        "name": "Mold",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709656,
            493.21637,
            537.296082,
            552.268921
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "14": {
        "choiceName": "",
        "groupName": "",
        "index": 14,
        "name": "Framing",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709625,
            420.615906,
            537.296021,
            479.668457
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "15": {
        "choiceName": "",
        "groupName": "",
        "index": 15,
        "name": "Electrical",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709625,
            345.880859,
            537.296021,
            404.933411
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "16": {
        "choiceName": "",
        "groupName": "",
        "index": 16,
        "name": "Plumbing",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709625,
            262.202148,
            537.296021,
            321.2547
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "17": {
        "choiceName": "",
        "groupName": "",
        "index": 17,
        "name": "Roof",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709694,
            177.291794,
            537.296082,
            236.344345
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "18": {
        "choiceName": "",
        "groupName": "",
        "index": 18,
        "name": "Foundation",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709625,
            92.1098022,
            537.296021,
            151.162354
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        },
        "19": {
        "choiceName": "",
        "groupName": "",
        "index": 19,
        "name": "HVAC",
        "pageHeight": 841.950012,
        "pageIndex": 0,
        "pageWidth": 595.349976,
        "rect": [
            120.709625,
            10.6740999,
            537.296021,
            69.7266541
        ],
        "singleSelectionOnly": False,
        "type": "text",
        "value": ""
        }
    }

extraction.fill_fields(fields)