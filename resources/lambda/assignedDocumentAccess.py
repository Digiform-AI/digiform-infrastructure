
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

def getAssignedDocument(documentId):
    cursor = connection.cursor()
    cursor.execute("SELECT d.document_name, d.document_path, a.assigned_date, a.assigned_by, a.assigned_to, a.document_assigned, a.completed_document FROM AssignedDocuments a INNER JOIN Documents d on a.document_assigned = d.document_id WHERE assigned_document_id = '{}'".format(documentId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()
    return json.dumps({
        "document_name": results[0][0], 
        "document_path": results[0][1], 
        "assigned_date": results[0][2], 
        "assigned_by": results[0][3], 
        "assigned_to": results[0][4], 
        "document_assigned": results[0][5], 
        "completed_document": results[0][6]
    }, default=str)

def getDocumentsAssignedByUser(userId):
    cursor = connection.cursor()
    cursor.execute("SELECT d.document_name, d.document_path, a.assigned_date, a.assigned_by, a.assigned_to, a.document_assigned, a.completed_document FROM AssignedDocuments a INNER JOIN Documents d on a.document_assigned = d.document_id  WHERE assigned_by = '{}'".format(userId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()

    output = []
    for document in results:
        output.append({
        "document_name": document[0], 
        "document_path": document[1], 
        "assigned_date": document[2], 
        "assigned_by": document[3], 
        "assigned_to": document[4], 
        "document_assigned": document[5], 
        "completed_document": document[6]
    })
    return json.dumps(output, default=str)

def getDocumentsAssignedToUser(userId):
    cursor = connection.cursor()
    cursor.execute("SELECT d.document_name, d.document_path, a.assigned_date, a.assigned_by, a.assigned_to, a.document_assigned, a.completed_document FROM AssignedDocuments a INNER JOIN Documents d on a.document_assigned = d.document_id  WHERE assigned_to = '{}'".format(userId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()
    output = []
    for document in results:
        output.append({
        "document_name": document[0], 
        "document_path": document[1], 
        "assigned_date": document[2], 
        "assigned_by": document[3], 
        "assigned_to": document[4], 
        "document_assigned": document[5], 
        "completed_document": document[6]
    })
    return json.dumps(output, default=str)

def getUsersAssignedToDocument(documentId):
    cursor = connection.cursor()
    cursor.execute("SELECT u.user_id, u.first_name, u.last_name, u.email FROM AssignedDocuments a INNER JOIN Users u on a.assigned_to = u.user_id WHERE assigned_document_id = '{}'".format(documentId))
    results = cursor.fetchall()
    cursor.close()
    connection.commit()

    output = []
    for user in results: 
        output.append({
            "user_id": user[0],
            "first_name": user[1],
            "last_name": user[2],
            "email": user[3],
            "phone": user[4],
        })
    return json.dumps(output, default=str)

def assignDocument(document):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO AssignedDocuments (assigned_date, assigned_by, assigned_to, document_assigned, completed_document) " + 
                    "VALUES ('{}', '{}', '{}', '{}', '{}')".format(document['assigned_date'], document['assigned_by'], document['assigned_to'], document['document_assigned'], ""))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'

def updateAssignedDocument(documentId, document):
    cursor = connection.cursor()
    cursor.execute("UPDATE AssignedDocuments SET completed_document = '{}' WHERE assigned_document_id = '{}'".format(document['completed_document'],documentId))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'