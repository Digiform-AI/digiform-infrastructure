
import os
import json
import boto3
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

def getUser(userEmail):
    print('Get User')
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, first_name, last_name, email, phone FROM Users u WHERE u.email = '{}'".format(userEmail))
    results = cursor.fetchall()
    print('Fetch call made')
    cursor.close()
    connection.commit()
    print('Return Data')
    return json.dumps({
        "user_id": results[0][0],
        "first_name": results[0][1],
        "last_name": results[0][2],
        "email": results[0][3],
        "phone": results[0][4],
    }, default=str) 

def getUsers():
    cursor = connection.cursor()
    cursor.execute("SELECT user_id, first_name, last_name, email, phone FROM Users")
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


def updateUser(userEmail, userData):
    cursor = connection.cursor()

    # update the user's information for first and last name, email and phone. 
    cursor.execute("UPDATE Users " +
                    "SET first_name = '{}', last_name = '{}', phone = '{}' " + 
                    "WHERE email = '{}'".format(userData['first_name'], userData['last_name'], userData['phone'], userEmail))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'


def insertUser(userData):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Users (first_name,last_name,email,phone,joined_date,tenant_key) VALUES ('{}','{}','{}','{}','{}','{}')".format(userData['first_name'],userData['last_name'],userData['email'],userData['phone'],userData['joined_date'],userData['tenant_key']))
    connection.commit()
    cursor.close()
    connection.commit()
    return 'success'