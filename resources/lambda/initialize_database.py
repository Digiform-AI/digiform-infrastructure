
import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters

# script to clear the database
clear_db = '''DELETE FROM Documents;
    DELETE FROM Users;
    DELETE FROM AssignedDocuments;
    
    DROP TABLE AssignedDocuments;
    DROP TABLE Documents;
    DROP TABLE Users;'''

# script to insert fake data into the database
fake_data ='''INSERT INTO Users (first_name,last_name,email,phone,joined_date,tenant_key) VALUES 
    ('Jon','Callahan','jcall@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Susie','Dubster','sdubster@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Mary','Churchill','mchurch@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Steve','Douglas','sdoug@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Annie','Smith','asmith@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Anna','Schwartz','asch@gmail.com','9177675583','June 6 2022','TK-1'),
    ('Callie','Ribeck','crib@gmail.com','9177675583','June 6 2022','TK-1'),
    ('David','Wellington','dwellington@gmail.com','9177675583','June 6 2022','TK-1');

    INSERT INTO Documents (document_name, document_path, created_date,created_by) VALUES
    ('Contract','https://neuro-exed-images.s3.amazonaws.com/tst/testing.pdf','June 01 2022',2),
    ('Paper','https://neuro-exed-images.s3.amazonaws.com/tst/testing.pdf','June 01 2022',2),
    ('Agreement','https://neuro-exed-images.s3.amazonaws.com/tst/testing.pdf','June 01 2022',2),
    ('Document','https://neuro-exed-images.s3.amazonaws.com/tst/testing.pdf','June 01 2022',2);
    
    INSERT INTO AssignedDocuments (assigned_date,assigned_by,assigned_to,document_assigned) VALUES
    ('February 10 2023',1,2,1),
    ('February 10 2023',1,2,2),
    ('February 10 2023',1,3,1),
    ('February 10 2023',1,3,2);'''

# script to create the database
schema = '''CREATE TABLE Tenants(
        tenant_id SERIAL PRIMARY KEY,
        name VARCHAR(90) NOT NULL,
        logo VARCHAR(80) NOT NULL
    );

    CREATE TABLE Users(
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(11) NULL,
        joined_date TIMESTAMP NOT NULL,
        tenant_key VARCHAR(20) NOT NULL	
    );

    CREATE TABLE Roles(
        role_id SERIAL PRIMARY KEY,
        role_name VARCHAR(30) NOT NULL
    );

    CREATE TABLE Permissions(
        permission_id SERIAL PRIMARY KEY,
        resource VARCHAR(50) NOT NULL,
        access VARCHAR(5) NOT NULL
    );

    CREATE TABLE UserRoles(
        user_role_id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        role_id INT NOT NULL
    );

    CREATE TABLE Documents(
        document_id SERIAL PRIMARY KEY,
        document_name VARCHAR(40) NOT NULL,
        document_path VARCHAR(300) NOT NULL,
        created_date TIMESTAMP NOT NULL,
        created_by INT NOT NULL,
        CONSTRAINT FK_creator FOREIGN KEY (created_by) REFERENCES Users(user_id)
    );

    CREATE TABLE AssignedDocuments(
        assigned_document_id SERIAL PRIMARY KEY,
        assigned_date TIMESTAMP NOT NULL,
        assigned_by INT NOT NULL,
        assigned_to INT NOT NULL,
        document_assigned INT NOT NULL,
        completed_document VARCHAR(300) NULL,
        CONSTRAINT FK_document FOREIGN KEY (assigned_by) REFERENCES Users(user_id),
        CONSTRAINT FK_assignee FOREIGN KEY (assigned_to) REFERENCES Users(user_id),
        CONSTRAINT FK_assigner FOREIGN KEY (document_assigned) REFERENCES Documents(document_id)
    );'''




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
        res = 'success'
        cursor = connection.cursor()
        
        if event['action'] == 'CLEAR':
            cursor.execute(clear_db)
        elif event['action'] == 'DEFINE':
            cursor.execute(schema)
        elif event['action'] == 'FILL':
            cursor.execute(fake_data)
        elif event['action'] == 'QUERY':
            cursor.execute(event['query'])

        res = cursor.fetchall()

        cursor.close()
        connection.commit()

        return {
            'statusCode': 200,
            'body':json.dumps(res, default=str)
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }