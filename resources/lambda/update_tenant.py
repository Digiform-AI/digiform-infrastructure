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

        # update the name and logo for a Tenant (Company)
        cursor.execute("UPDATE Tenants " +
                       "SET name = '{}', logo = '{}' " + 
                       "WHERE tenant_id = '{}'".format(event.new_tenant_name, event.new_tenant_logo, event.tenant_id))
        connection.commit()
        cursor.close()
        connection.commit()

        return {
            'Access-Control-Allow-Origin': '*',
            'statusCode': 200,
            'body' : "Successfully Updated Tenant (Comapany) Name and Logo"
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': str(e)
        }