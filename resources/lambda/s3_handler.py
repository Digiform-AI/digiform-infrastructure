import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters

s3 = boto3.client('s3')

def lambda_handler(event, context):   
    file_name = event['filename']
    bucket_name = os.environ.get("BUCKET")

    try:
        if(event['action'] == 'PUSH'):
            s3.upload_file(file_name, bucket_name, file_name)
            return {
                'statusCode': 200,
                'body': 'File uploaded successfully'
            }
        else:
            file_object = s3.get_object(Bucket=bucket_name, Key=file_name)
            file_content = file_object['Body'].read()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-type': 'application/pdf',
                    'Content-Disposition': 'attachment; filename="example_file.pdf"'
                },
                'body': file_content,
                'isBase64Encoded': True
            }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }