import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters

s3 = boto3.client('s3')

def lambda_handler(event, context):   
    file_name = event['file_name']
    bucket_name = os.environ.get("BUCKET")

    try:
        if(event['action'] == 'PUSH'):
            file_content = event['file_content']
            s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
                },
                'body': 'File uploaded successfully'
            }
        else:
            file_object = s3.get_object(Bucket=bucket_name, Key=file_name)
            file_content = file_object['Body'].read()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-type': 'application/pdf',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True,
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