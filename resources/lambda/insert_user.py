
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

        cursor.execute("INSERT INTO Users (first_name,last_name,email,phone,joined_date,tenant_key) VALUES ('{}','{}','{}','{}','{}','{}')".format(event['first_name'],event['last_name'],event['email'],event['phone'],event['joined_date'],event['tenant_key']))
        connection.commit()
        cursor.close()
        connection.commit()

        return {
            'Access-Control-Allow-Origin': '*',
            'statusCode': 200,
            'body':'successfully inserted user'
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }