
import os
import json
import psycopg2
from aws_lambda_powertools.utilities import parameters

SECRET = json.loads(parameters.get_secret(os.environ.get("DB_SECRET_NAME")))

connection = psycopg2.connect(
    database=SECRET.get("engine"),
    user=SECRET.get("username"),
    password=SECRET.get("password"),
    host=SECRET.get("host"),
    port="5432",
)

def getDocument(documentId):
    cursor = connection.cursor()
    cursor.execute("SELECT document_name, document_path, created_date, created_by FROM Documents WHERE document_id = '{}'".format(documentId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()
    return json.dumps({
        "document_name": results[0][0], 
        "document_path": results[0][1], 
        "created_date": results[0][2], 
        "created_by": results[0][3]
    }, default=str)

def getUserDocuments(userId):
    cursor = connection.cursor()
    cursor.execute("SELECT document_name, document_path, created_date FROM Documents WHERE created_by = '{}'".format(userId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()

    output = []
    for document in results:
        output.append({
            "document_name": document[0], 
            "document_path": document[1], 
            "created_date": document[2], 
        })
    return json.dumps(output, default=str)

def insertDocument(document):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Documents (document_name,document_path,created_date,created_by) VALUES ('{}','{}','{}','{}')".format(document['document_name'],document['document_path'],document['created_date'],document['created_by']))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'

def updateDocument(documentId, document):
    cursor = connection.cursor()
    cursor.execute("UPDATE Documents SET document_name = '{}',document_path = '{}', created_date = '{}', created_by = '{}' WHERE document_id = '{}'".format(document['document_name'],document['document_path'],document['created_date'],document['created_by'],documentId))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'