#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DigiformStack } from '../lib/aws-cdk-example-stack';

const app = new cdk.App();
new DigiformStack(app, 'DigiformStack', {

});