import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters

def lambda_handler(event, context):   
    SECRET = json.loads(parameters.get_secret(os.environ.get("DB_SECRET_NAME")))

    connection = psycopg2.connect(
        database=SECRET.get("engine"),
        user=SECRET.get("username"),
        password=SECRET.get("password"),
        host=SECRET.get("host"),
        port="5432",
    )

    try:
        cursor = connection.cursor()

        # get all documents assigned to a specifc user by user ID
        cursor.execute("SELECT * FROM AssignedDocuments WHERE user_id = '{}'".format(event.user_id))
        results = cursor.fetchall()
        cursor.close()
        connection.commit()

        return {
            'Access-Control-Allow-Origin': '*',
            'statusCode': 200,
            'body' : str(results) 
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }