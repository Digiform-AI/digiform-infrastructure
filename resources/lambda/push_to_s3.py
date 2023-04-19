import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters

s3 = boto3.client('s3')

def lambda_handler(event, context):   
    file_name = event['filename']
    bucket_name = "DigiformStore"

    # Get the file data from the request body
    file_data = event['body'].encode('utf-8') # assuming that file is sent as string
    
    # Upload the file to S3
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_data)

    try:


        return {
            'statusCode': 200,
            'body':'Success'
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }