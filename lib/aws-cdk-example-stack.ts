import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { aws_ec2 as ec2 } from 'aws-cdk-lib';
import { aws_rds as rds } from 'aws-cdk-lib';
import { aws_s3 as s3 } from 'aws-cdk-lib';
import { aws_apigateway as apigateway } from 'aws-cdk-lib';
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha';
import { Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration } from 'aws-cdk-lib';


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
						// (only the outbound connections from your private subnet to the internet)
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
		});

		const databaseName = 'digiformDatabase';
		const dbInstance = new rds.DatabaseInstance(this, 'Instance', {
			engine: rds.DatabaseInstanceEngine.postgres({
				version: rds.PostgresEngineVersion.VER_13,
			}),
			// optional, defaults to m5.large
			instanceType: ec2.InstanceType.of(
				ec2.InstanceClass.BURSTABLE3,
				ec2.InstanceSize.SMALL
			),
			vpc,
			vpcSubnets: vpc.selectSubnets({
				subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
			}),
			databaseName,
			securityGroups: [dbSecurityGroup],
			credentials: rds.Credentials.fromGeneratedSecret('postgres'), // Generates usr/pw in secrets manager
			maxAllocatedStorage: 200, // Storage for DB in GB
		});

		// create the RDS Proxy and add the database instance as the proxy target.
		const dbProxy = new rds.DatabaseProxy(this, 'Proxy', {
			proxyTarget: rds.ProxyTarget.fromInstance(dbInstance),
			secrets: [dbInstance.secret!],
			securityGroups: [dbSecurityGroup],
			vpc,
			requireTLS: false,
			vpcSubnets: vpc.selectSubnets({
			  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
			}),
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
		const autoScalingLambda = new PythonFunction(this, 'Initialize DB', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_8,
			index: 'initialize_database.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbProxy.endpoint,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5), 
			vpc,
			vpcSubnets: vpc.selectSubnets({
			  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
			}),
			securityGroups: [lambdaSG],
		});

		// define textract lambda
		const textractLambda = new PythonFunction(this, 'FileReader', {
			entry: './resources/lambda/',
			runtime: Runtime.PYTHON_3_7,
			index: 'search_pdf.py',
			handler: 'lambda_handler',
			environment: {
				DB_ENDPOINT_ADDRESS: dbProxy.endpoint,
				DB_NAME: databaseName,
				DB_SECRET_ARN: dbInstance.secret?.secretFullArn || '',
				DB_SECRET_NAME: dbInstance.secret?.secretName!,
				BUCKET: bucket.bucketName,
			},
			timeout: Duration.minutes(5), 
			vpc,
			vpcSubnets: vpc.selectSubnets({
			  subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS,
			}),
			securityGroups: [lambdaSG],
		});

		/*
			ACCESS SPECIFICATIONS
		*/
		//scaling lambda
		dbInstance.secret?.grantRead(autoScalingLambda);
		dbInstance.secret?.grantWrite(autoScalingLambda);
		bucket.grantReadWrite(autoScalingLambda);

		//textraxt lambda
		dbInstance.secret?.grantRead(textractLambda);
		dbInstance.secret?.grantWrite(textractLambda);
		bucket.grantReadWrite(textractLambda);



		// limit traffic to DB to port 5432
		dbSecurityGroup.addIngressRule(
			lambdaSG,
			ec2.Port.tcp(5432),
			'Lambda to Postgres database'
		);


		/*
			API SPECIFICATIONS
		*/
		
		// api gateway instance
		const api = new apigateway.RestApi(this, "digiform-api", {
			restApiName: "Widget Service",
			description: "This service serves widgets."
		});

		// lambda integration
		const getFilesIntegration = new apigateway.LambdaIntegration(autoScalingLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const textractIntegration = new apigateway.LambdaIntegration(autoScalingLambda, {
			requestTemplates: { "application/json": '{ "statusCode": "200" }' }
		});

		const files = api.root.addResource('files');
		files.addMethod("GET", getFilesIntegration);

		const pdf = api.root.addResource('pdf');
		pdf.addMethod("GET", textractIntegration);
	}
}
