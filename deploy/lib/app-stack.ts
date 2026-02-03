import * as cdk from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
// import * as lambda from 'aws-cdk-lib/aws-lambda';
// import * as apigatewayv2 from 'aws-cdk-lib/aws-apigatewayv2';
// import * as integrations from 'aws-cdk-lib/aws-apigatewayv2-integrations';
// import * as s3 from 'aws-cdk-lib/aws-s3';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class AppStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    //一个VPC（10.0.x.x）
    const vpc = new ec2.Vpc(this, 'my-rag-vpc', {
      ipAddresses: ec2.IpAddresses.cidr('10.0.0.0/16'),
      maxAzs: 1,
      subnetConfiguration: [
        {
          name: 'public-0',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
      ],
    });
    void vpc;

    //在VPC里面创建一个Cluster
    const cluster = new ecs.Cluster(this, 'my-rag-cluster', {
      vpc: vpc
    });
    void cluster;

    //独立定义一个Task（可以含多个Containers）
    const task0 = new ecs.FargateTaskDefinition(this, 'my-rag-task-0', {
      family: 'my-rag'
    });
    task0.addContainer('my-rag-container-0', {
      cpu: 256,
      memoryLimitMiB: 512,
      image: ecs.ContainerImage.fromAsset('/app', { file: 'Dockerfile-my-rag-container-0' }),
      portMappings: [{ containerPort: 8000, protocol: ecs.Protocol.TCP }],
      environment: {
        NVIDIA_API_KEY: process.env.NVIDIA_API_KEY || '',
        EMBEDDING_MODEL: process.env.EMBEDDING_MODEL || '',
        LLM_MODEL: process.env.LLM_MODEL || '',
      }
    })
    void task0;

    //在VPC里面创建一个SG
    const sg0 = new ec2.SecurityGroup(this, 'my-rag-sg-0', {
      vpc: vpc,
    });
    sg0.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(8000));
    sg0.addEgressRule(ec2.Peer.anyIpv4(), ec2.Port.allTcp());
    void sg0;

    //在Cluster里部署这个Task
    const service0 = new ecs.FargateService(this, 'my-rag-cluster-task-0', {
      cluster: cluster,
      taskDefinition: task0,
      securityGroups: [sg0],
      assignPublicIp: true,
      vpcSubnets: {
        subnetType: ec2.SubnetType.PUBLIC
      }
    })
    void service0;
  }
}
