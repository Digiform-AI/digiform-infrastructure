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
import {  Peer, Port } from 'aws-cdk-lib/aws-ec2';


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
			publiclyAccessible:true,
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

		// lambda security group
		const lambdaSG = new ec2.SecurityGroup(this, 'LambdaSG', {
			vpc,
		});

		// define sample lambda
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

		// define sample lambda
		const autoScalingLambda = new PythonFunction(this, 'Initialize DB', {
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

		// define textract lambda
		const textractLambda = new PythonFunction(this, 'FileReader', {
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

		// define textract lambd
		const fetchUsersLambda = new PythonFunction(this, 'FetchUsers', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'fetch_users.py',
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


		// define fetch user lambda
		const fetchUserLambda = new PythonFunction(this, 'FetchUser', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'fetch_user.py',
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

		// define insert user lambda
		const insertUserLambda = new PythonFunction(this, 'InsertUser', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'insert_user.py',
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

		// define insert documents lambda
		const insertDocumentsLambda = new PythonFunction(this, 'InsertDocuments', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'insert_user.py',
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

		// define textract lambda
		const fetchDocumentsLambda = new PythonFunction(this, 'FetchDocuments', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_9,
			index: 'fetch_documents.py',
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

		const generatePrintPdfLambda = new PythonFunction(this, 'GeneratePrintPdf', {
			entry: './resources/lambda/pdf',
			runtime: Runtime.PYTHON_3_9,
			index: 'generate_print_pdf.py',
			handler: 'lambda_handler',
			environment: {
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5), 
			vpc,
			securityGroups: [lambdaSG],
		});

		const generatePrintPdfFromKeysLambda = new PythonFunction(this, 'GeneratePrintPdfFromKeys', {
			entry: './resources/lambda/pdf',
			runtime: Runtime.PYTHON_3_9,
			index: 'generate_pdf_from_keys.py',
			handler: 'lambda_handler',
			environment: {
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5), 
			vpc,
			securityGroups: [lambdaSG],
		});

		/*
			ACCESS SPECIFICATIONS
		*/
		//scaling lambda
		dbInstance.secret?.grantRead(autoScalingLambda);
		dbInstance.secret?.grantWrite(autoScalingLambda);
		bucket.grantReadWrite(autoScalingLambda);

		//scaling lambda
		dbInstance.secret?.grantRead(queryLambda);
		dbInstance.secret?.grantWrite(queryLambda);
		bucket.grantReadWrite(queryLambda);

		//textraxt lambda
		dbInstance.secret?.grantRead(textractLambda);
		dbInstance.secret?.grantWrite(textractLambda);
		bucket.grantReadWrite(textractLambda);

		//fetch users lambda
		dbInstance.secret?.grantRead(fetchUsersLambda);
		dbInstance.secret?.grantWrite(fetchUsersLambda);
		bucket.grantReadWrite(fetchUsersLambda);

		//fetch users lambda
		dbInstance.secret?.grantRead(fetchUserLambda);
		dbInstance.secret?.grantWrite(fetchUserLambda);
		bucket.grantReadWrite(fetchUserLambda);

		//fetch documents lambda
		dbInstance.secret?.grantRead(fetchDocumentsLambda);
		dbInstance.secret?.grantWrite(fetchDocumentsLambda);
		bucket.grantReadWrite(fetchDocumentsLambda);

		//insert user lambda
		dbInstance.secret?.grantRead(insertUserLambda);
		dbInstance.secret?.grantWrite(insertUserLambda);
		bucket.grantReadWrite(insertUserLambda);

		bucket.grantReadWrite(generatePrintPdfLambda);
		bucket.grantReadWrite(generatePrintPdfFromKeysLambda);

		// limit traffic to DB to port 5432
		dbSecurityGroup.addIngressRule(
			lambdaSG,
			ec2.Port.tcp(5432),
			'Lambda to Postgres database'
		);

		/*
			API SPECIFICATIONS
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


		// lambda integration
		const queryIntegration = new apigateway.LambdaIntegration(queryLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		// lambda integration
		const getFilesIntegration = new apigateway.LambdaIntegration(autoScalingLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const textractIntegration = new apigateway.LambdaIntegration(textractLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const fetchUsersIntegration = new apigateway.LambdaIntegration(fetchUsersLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const insertUserIntegration = new apigateway.LambdaIntegration(insertUserLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const fetchDocumentsIntegration = new apigateway.LambdaIntegration(fetchDocumentsLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const generatePrintPdfIntegration = new apigateway.LambdaIntegration(generatePrintPdfLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});
		const generatePrintPdfFromKeysIntegration = new apigateway.LambdaIntegration(generatePrintPdfFromKeysLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const query = api.root.addResource('query', {
			defaultCorsPreflightOptions: cors
		});
		query.addMethod("POST", queryIntegration);

		const files = api.root.addResource('files', {
			defaultCorsPreflightOptions: cors
		});
		files.addMethod("GET", getFilesIntegration);


		const pdf = api.root.addResource('pdf', {
			defaultCorsPreflightOptions: cors
		});
		pdf.addMethod("GET", textractIntegration);

		const users = api.root.addResource('users', {
			defaultCorsPreflightOptions: cors
		});
		users.addMethod("GET", fetchUsersIntegration);

		const user = api.root.addResource('user', {
			defaultCorsPreflightOptions: cors
		});
		user.addMethod("GET", fetchUsersIntegration);
		user.addMethod("POST", insertUserIntegration);

		const documents = api.root.addResource('documents', {
			defaultCorsPreflightOptions: cors
		});
		documents.addMethod("GET", fetchDocumentsIntegration);

		const pdfFunctions = api.root.addResource('generatePrintPdf', {
			defaultCorsPreflightOptions: cors
		});
		pdfFunctions.addMethod("POST", generatePrintPdfIntegration);

		const generatePrintPdfFromKeysFunction = api.root.addResource('generatePdfFromKeys', {
			defaultCorsPreflightOptions: cors
		});
		generatePrintPdfFromKeysFunction.addMethod("POST", generatePrintPdfFromKeysIntegration);
		

		/*
			COGNITO
		*/
		const userPool = new cognito.UserPool(this, 'userpool', {
			userPoolName: 'digiform-user-pool',
			selfSignUpEnabled: true,
			signInAliases: {
			  email: true,
			},
			autoVerify: {
			  email: true,
			},
			standardAttributes: {
			  givenName: {
				required: true,
				mutable: true,
			  },
			  familyName: {
				required: true,
				mutable: true,
			  },
			},
			customAttributes: {
			  country: new cognito.StringAttribute({mutable: true}),
			  city: new cognito.StringAttribute({mutable: true}),
			  isAdmin: new cognito.StringAttribute({mutable: true}),
			},
			passwordPolicy: {
			  minLength: 6,
			  requireLowercase: true,
			  requireDigits: true,
			  requireUppercase: false,
			  requireSymbols: false,
			},
			accountRecovery: cognito.AccountRecovery.EMAIL_ONLY,
			removalPolicy: cdk.RemovalPolicy.RETAIN,
		});

		const standardCognitoAttributes = {
			givenName: true,
			familyName: true,
			email: true,
			emailVerified: true,
			address: true,
			birthdate: true,
			gender: true,
			locale: true,
			middleName: true,
			fullname: true,
			nickname: true,
			phoneNumber: true,
			phoneNumberVerified: true,
			profilePicture: true,
			preferredUsername: true,
			profilePage: true,
			timezone: true,
			lastUpdateTime: true,
			website: true,
		};
		  
		const clientReadAttributes = new cognito.ClientAttributes()
			.withStandardAttributes(standardCognitoAttributes)
			.withCustomAttributes(...['country', 'city', 'isAdmin']);
		  
		const clientWriteAttributes = new cognito.ClientAttributes()
			.withStandardAttributes({
			  ...standardCognitoAttributes,
			  emailVerified: false,
			  phoneNumberVerified: false,
		})
		.withCustomAttributes(...['country', 'city']);
		  
		const userPoolClient = new cognito.UserPoolClient(this, 'userpool-client', {
			userPool,
			authFlows: {
			  adminUserPassword: true,
			  custom: true,
			  userSrp: true,
			},
			supportedIdentityProviders: [
			  cognito.UserPoolClientIdentityProvider.COGNITO,
			],
			readAttributes: clientReadAttributes,
			writeAttributes: clientWriteAttributes,
		});

		new cdk.CfnOutput(this, 'userPoolId', {
			value: userPool.userPoolId,
		});
		new cdk.CfnOutput(this, 'userPoolClientId', {
			value: userPoolClient.userPoolClientId,
		});
	}
}
