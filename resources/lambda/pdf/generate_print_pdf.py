import boto3
import os
from botocore.exceptions import ClientError
from pypdf import PdfReader, PdfWriter
from pypdf.generic import BooleanObject, NameObject, IndirectObject, TextStringObject, NumberObject
from pypdf.constants import *
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfform
from reportlab.lib.colors import magenta, pink, blue, green
import os, io
import shutil

from pdfStructure import pdfForm, pdfElement, Consts

s3 = boto3.client('s3')

def lambda_handler(event, context):   
    """
        params:
            [event.filename]
    """

    BUCKET_NAME = os.environ.get("BUCKET")
    KEY = 'test.pdf'
    LOCAL_PATH = '/{}'.format(KEY)
    # fetch pdf from event.filename

    print('STARTING')

    try:
        print('FETCHING')

        s3.download_file(BUCKET_NAME, KEY, LOCAL_PATH)

        print('FETCHED')

        with open(LOCAL_PATH, 'r') as printFile:
            print('SUCCESS. file opened')

            newPath = printFile.path.replace(".pdf", "-print.pdf")
            shutil.copy(printFile.path, newPath) # Create a copy to put the boxes onto
            
            # Set up a new blank file to draw rectangles on
            packet = io.BytesIO()
            can = canvas.Canvas(packet)

            existing_pdf = PdfReader(open(newPath, "rb")) # Store the existing pdf, the copy which we will overlay the boxes to
            output = PdfWriter() # designate a file for the final output

            
            # For each page, generate a page on a new buffer of just boxes. Later, we overlay the two.
            for i in range(len(existing_pdf.pages)):
                w, h = 0, 0
                
                # Make each border for a field on this page, only
                for field in printFile.fields:
                    if field.pageIndex == i: # Make sure this field is on this page!
                        can.rect(field.rect[0], field.rect[1], field.rect[2] - field.rect[0], field.rect[3] - field.rect[1])
                        w, h = field.pageWidth, field.pageHeight # Save this page's width and height to draw a surround box

                # Make border around entire page (for cropping), independent of print margin settings
                can.setLineWidth(2)
                can.rect(0,0,w,h)
                

                can.showPage() # end the page
                
                packet.seek(0)
                
            
            can.save() # save the pdf
            new_pdf = PdfReader(packet) # Store the pdf containing only rectangles

            # Merge all pages together
            for i in range(len(existing_pdf.pages)):
                
                page = existing_pdf.pages[i]
                page.merge_page(new_pdf.pages[i])
                output.add_page(page)
                
            outputStream = open(newPath, "wb")
            output.write(outputStream)
            outputStream.close()

            # push to s3
            s3.upload_file(newPath, BUCKET_NAME, newPath)

            print('file uploaded')

            return {
                'statusCode': 200,
                'body': newPath
            }


    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            print("Unknown error: {}".format(e))

        return {
            'statusCode': 404,
            'body': 'File not found!'
        }

    except Exception as e:
        print("Unexpected error: {}".format(e))

        return {
            'statusCode': 500,
            'body': 'Error downloading file!'
        }

    