
import os
import json
import boto3
import psycopg2
from aws_lambda_powertools.utilities import parameters


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
    ('Document','https://neuro-exed-images.s3.amazonaws.com/tst/testing.pdf','June 01 2022',2);'''

schema = '''CREATE TABLE Users(
        user_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        email VARCHAR(100) NOT NULL,
        phone VARCHAR(11) NULL,
        joined_date TIMESTAMP NOT NULL,
        tenant_key VARCHAR(20) NOT NULL	
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
        cursor = connection.cursor()
        print("connection established- attempt")
        print(cursor)
        print(schema)
        print(fake_data)

        cursor.execute(schema)
        cursor.execute(fake_data)
        cursor.execute("SELECT * FROM Users")
        results = cursor.fetchall()
        print(results)
        cursor.close()
        connection.commit()

        return {
            'statusCode': 200,
            'body':str(results) 
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }