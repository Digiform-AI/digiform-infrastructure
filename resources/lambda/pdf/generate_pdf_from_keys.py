import boto3
import os
from botocore.exceptions import ClientError
from pypdf import PdfReader, PdfWriter
from pdfManager import PdfGenerator
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
    BUCKET_NAME = os.environ.get("BUCKET")

    print("STARTING")
    print(event)

    fields = []
    for i, field in enumerate(event['fields']):
        if field['type'] == 'TEXT':
            print('text')
            fields.append(pdfElement(field['name'], Consts.textFieldDisplay, "", i, None, True, None, None, 0))
        elif field['type'] == 'MULTIPLE':
            print('MULTI')
            fields.append(pdfElement(field['name'], Consts.mcDisplay, "", i, None, True, None, None, 0))
        elif field['type'] == 'CHECKBOX':
            print('CHECK')
            fields.append(pdfElement(field['name'], Consts.checkBoxDisplay, "", i, None, True, None, None, 0))

    newForm = PdfGenerator.createPdf(fields,event['title'])

    s3.upload_file(newForm.path, BUCKET_NAME, newForm.path)

    print('file uploaded')

    return {
        'statusCode': 200,
        'body': newForm.path
    }


    