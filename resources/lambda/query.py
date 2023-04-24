
import os
import json
import psycopg2
from aws_lambda_powertools.utilities import parameters
import userAccess as users
import documentAccess as documents
import assignedDocumentAccess as assignedDocuments

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
        print('entered')
        
        resource = json.loads(event['body'])['resource']
        command = json.loads(event['body'])['command']
        request = json.loads(event['body'])['request']

        response = ''
        if(resource == 'Users'):
            if(command == 'GET'):
                response = users.getUser(request['email'])
            elif(command == 'GETALL'):
                response = users.getUsers()
            if(command == 'UPDATE'):
                response = users.updateUser(request['email'], request['user'])
            if(command == 'INSERT'):
                response = users.insertUser(request['user'])
        elif(resource == 'Documents'):
            if(command == 'GET'):
                response = documents.getDocument(request['documentId'])
            elif(command == 'GETALL'):
                response = documents.getUserDocuments(request['userId'])
            if(command == 'UPDATE'):
                response = documents.updateDocument(request['documentId'], request['document'])
            if(command == 'INSERT'):
                response = documents.insertDocument(request['document'])
        elif(resource == 'AssignedDocuments'):
            if(command == 'GET'):
                response = assignedDocuments.getAssignedDocument(request['documentId'])
            elif(command == 'GET_ASSIGNED_BY'):
                response = assignedDocuments.getDocumentsAssignedByUser(request['userId'])
            elif(command == 'GET_ASSIGNED_TO'):
                response = assignedDocuments.getDocumentsAssignedToUser(request['userId'])
            elif(command == 'GET_ASSIGNED_USERS'):
                response = assignedDocuments.getUsersAssignedToDocument(request['documentId'])
            if(command == 'UPDATE'):
                response = assignedDocuments.updateAssignedDocument(request['documentId'], request['document'])
            if(command == 'INSERT'):
                response = assignedDocuments.assignDocument(request['document'])

        cursor.close()
        connection.commit()

        print('return val')
        print(json.dumps(response))

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True,
            },
            'body': json.dumps(response)
        }
    except Exception as e:
        print('error occurred')
        print(e)
        return {
            'statusCode': 400,
            'body': str(e)
        }