import * as cognito from 'aws-cdk-lib/aws-cognito';
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_ec2 as ec2 } from 'aws-cdk-lib';
import { aws_rds as rds } from 'aws-cdk-lib';
import { aws_s3 as s3 } from 'aws-cdk-lib';
import { aws_apigateway as apigateway } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';
import { Cors } from 'aws-cdk-lib/aws-apigateway';
import { Peer, Port } from 'aws-cdk-lib/aws-ec2';


export class DigiformStack extends cdk.Stack {
	constructor(scope: Construct, id: string, props?: cdk.StackProps) {
		super(scope, id, props);

		/*
			VPC SPECIFICATIONS
		*/

		const vpc = new ec2.Vpc(this, 'digiformVPC', {
			maxAzs: 2,
			subnetConfiguration: [
				{
					cidrMask: 24,
					name: 'Private',
					subnetType: ec2.SubnetType.PRIVATE_ISOLATED,
				},
				{
					cidrMask: 24,
					name: 'privatelambda',
					subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
					//creates a NAT Gateway and will place that NAT Gateway in the public subnet. 
				},
				{
					cidrMask: 24,
					name: 'public',
					subnetType: ec2.SubnetType.PUBLIC,
				},
			],
		});

		/*
			DB SPECIFICATIONS
		*/

		// security group controls access to DB (IPs and port)
		const dbSecurityGroup = new ec2.SecurityGroup(this, 'DbSecurityGroup', {
			vpc,
			allowAllOutbound: true
		});

		dbSecurityGroup.addEgressRule(Peer.anyIpv4(), Port.allTraffic())
		dbSecurityGroup.addIngressRule(Peer.anyIpv4(), Port.allTraffic())

		const databaseName = 'digiformDatabase';
		const dbInstance = new rds.DatabaseInstance(this, 'Instance', {
			engine: rds.DatabaseInstanceEngine.postgres({
				version: rds.PostgresEngineVersion.VER_13,
			}),
			instanceType: ec2.InstanceType.of(
				ec2.InstanceClass.BURSTABLE3,
				ec2.InstanceSize.SMALL
			),
			vpc,
			databaseName,
			securityGroups: [dbSecurityGroup],
			publiclyAccessible: false,
			credentials: rds.Credentials.fromGeneratedSecret('postgres'), // Generates usr/pw in secrets manager
			maxAllocatedStorage: 100, // Storage for DB in GB
		});

		/*
			S3 SPECIFICATIONS
		*/

		// storage bucket
		const bucket = new s3.Bucket(this, "DigiformStore");

		/*
			LAMBDA SPECIFICATIONS
		*/
		const cors = {
			allowOrigins: apigateway.Cors.ALL_ORIGINS,
			allowMethods: apigateway.Cors.ALL_METHODS,
			allowHeaders: apigateway.Cors.DEFAULT_HEADERS,
		};

		// api gateway instance
		const api = new apigateway.RestApi(this, "digiform-api", {
			defaultCorsPreflightOptions: cors,
			restApiName: "Widget Service",
			description: "This service serves widgets."
		});

		// lambda security group
		const lambdaSG = new ec2.SecurityGroup(this, 'LambdaSG', {
			vpc,
			allowAllOutbound: true,
		});

		// limit traffic to DB to port 5432
		dbSecurityGroup.addIngressRule(
			lambdaSG,
			ec2.Port.tcp(5432),
			'Lambda to Postgres database'
		);

		const queryLambda = new PythonFunction(this, 'Query DB', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'query.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbInstance.dbInstanceEndpointAddress,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5),
			vpc,
			securityGroups: [lambdaSG],
		});

		dbInstance.secret?.grantRead(queryLambda);
		dbInstance.secret?.grantWrite(queryLambda);
		bucket.grantReadWrite(queryLambda);

		const queryIntegration = new apigateway.LambdaIntegration(queryLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' },


		});
		const query = api.root.addResource('query', {
			defaultCorsPreflightOptions: cors,

		});
		query.addMethod("POST", queryIntegration, {
			methodResponses: [{
				statusCode: '200',
			}],
		});



		const initDbLambda = new PythonFunction(this, 'Initialize DB', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'initialize_database.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbInstance.dbInstanceEndpointAddress,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5),
			vpc,
			securityGroups: [lambdaSG],
		});

		dbInstance.secret?.grantRead(initDbLambda);
		dbInstance.secret?.grantWrite(initDbLambda);
		bucket.grantReadWrite(initDbLambda);

		const initIntegration = new apigateway.LambdaIntegration(initDbLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});
		const init = api.root.addResource('init', {
			defaultCorsPreflightOptions: cors
		});
		init.addMethod("POST", initIntegration);




		const preparePdfLambda = new PythonFunction(this, 'Prepare PDF', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'prepare_pdf.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbInstance.dbInstanceEndpointAddress,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5),
			vpc,
			securityGroups: [lambdaSG],
		});

		dbInstance.secret?.grantRead(preparePdfLambda);
		dbInstance.secret?.grantWrite(preparePdfLambda);
		bucket.grantReadWrite(preparePdfLambda);

		const preparePdfIntegration = new apigateway.LambdaIntegration(preparePdfLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});
		const preparePdf = api.root.addResource('preparePdf', {
			defaultCorsPreflightOptions: cors
		});
		preparePdf.addMethod("POST", preparePdfIntegration);




		const searchPdfLambda = new PythonFunction(this, 'search PDF', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'search_pdf.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbInstance.dbInstanceEndpointAddress,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5),
			vpc,
			securityGroups: [lambdaSG],
		});

		dbInstance.secret?.grantRead(searchPdfLambda);
		dbInstance.secret?.grantWrite(searchPdfLambda);
		bucket.grantReadWrite(searchPdfLambda);

		const searchPdfIntegration = new apigateway.LambdaIntegration(searchPdfLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});
		const searchPdf = api.root.addResource('searchPdf', {
			defaultCorsPreflightOptions: cors
		});
		searchPdf.addMethod("POST", searchPdfIntegration);




		const pushPdfLambda = new PythonFunction(this, 'S3 handler', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 's3_handler.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbInstance.dbInstanceEndpointAddress,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5),
			vpc,
			securityGroups: [lambdaSG],
		});

		dbInstance.secret?.grantRead(pushPdfLambda);
		dbInstance.secret?.grantWrite(pushPdfLambda);
		bucket.grantReadWrite(pushPdfLambda);

		const pushPdfIntegration = new apigateway.LambdaIntegration(pushPdfLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});
		const pushPdf = api.root.addResource('pushPdf', {
			defaultCorsPreflightOptions: cors
		});
		pushPdf.addMethod("POST", pushPdfIntegration);
	}
}
