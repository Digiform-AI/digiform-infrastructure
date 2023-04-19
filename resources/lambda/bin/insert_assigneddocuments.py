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

        # Assign a document to a user by inserting to this table
        cursor.execute("INSERT INTO AssignedDocuments (assigned_date, assigned_by, assigned_to, document_assigned, completed_document) " + 
                       "VALUES ('{}', '{}', '{}', '{}', '{}')".format(event.date, event.assigned_by, event.assigned_to, event.doc_assigned, event.completed_doc))
        connection.commit()
        cursor.close()
        connection.commit()

        return {
            'Access-Control-Allow-Origin': '*',
            'statusCode': 200,
            'body' : "Successfully Assigned Document to User" 
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }