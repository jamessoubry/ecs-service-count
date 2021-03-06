# ecs-service-count
Docker container to adjust ECS service count to follow cluster instance count.

this is a simpler solution to the following:
  https://github.com/kgirthofer/service_shuffler
  https://github.com/blox/blox/tree/master/daemon-scheduler

## Env Variables
* SERVICE - (required) The name of the ECS service to update.
* CLUSTER - (optional) The Cluster to follow instance count. If omitted the service will attempt to resolve from the Cluster that the ECS task is running on.
* AWS_DEFAULT_REGION - (optional) The Region of the Cluster. If omitted the service will attempt to resolve from to the Region that the ECS task is running on.
* AWS_SECRET_ACCESS_KEY - if running on ECS this will be provided by the Service Role.
* AWS_ACCESS_KEY_ID - if running on ECS this will be provided by the Service Role.

* DAEMON - (optional) if you want to use CloudWatch Events to schedule this container then set this as False (Default: True)
* INTERVAL - (optional) api poll interval, in seconds (Default: 30)
* LOG_LEVEL - (optional) python log level e.g WARNING,CRITICAL,ERROR,INFO,DEBUG (Default: INFO)

## Recomendations
Use a placement constraints of  "distinctInstance" when launching your ECS service

##IAM Policy
The IAM Policy for the Service Role
```
{
    "Statement": [
        {
            "Action": [
                "ecs:DescribeClusters",
                "ecs:DescribeServices"
            ],
            "Resource": "*",
            "Effect": "Allow"
        },
        {
            "Action": [
                "ecs:UpdateService"
            ],
            "Resource": "arn:aws:ecs:eu-west-1:12345678:service/MyService",
            "Effect": "Allow"
        }
    ]
}
```

## Examples
Local Docker execution example:
```
export AWS_SECRET_ACCESS_KEY=1112233444555667778888
export AWS_ACCESS_KEY_ID=43543t4t435t43wefsdfsdfsdfsdf
export AWS_DEFAULT_REGION=eu-west-1

docker run -it \
-e AWS_SECRET_ACCESS_KEY \
-e AWS_ACCESS_KEY_ID \
-e AWS_DEFAULT_REGION \
-e CLUSTER=MyCluster \
-e SERVICE=MyService \
jamessoubry/ecs-service-count:latest
```


CloudFormation example:

```
Resources:
  ...

  ServiceCountService:
    Type: AWS::ECS::Service
    Properties:
      ServiceName: !Sub '${AWS::StackName}-service-count'
      Cluster: !Ref MyCluster
      DesiredCount: 1
      PlacementConstraints:
        - Type: distinctInstance
      DeploymentConfiguration:
        MaximumPercent: 100
        MinimumHealthyPercent: 0
      TaskDefinition: !Ref ServiceCountTaskDefinition

  ServiceCountrRole:
    Type: 'AWS::IAM::Role'
    Properties:
      RoleName: !Sub '${AWS::StackName}-service-count'
      AssumeRolePolicyDocument:
        Statement:
          - Effect: Allow
            Principal:
              Service:
                - ecs-tasks.amazonaws.com
            Action:
              - 'sts:AssumeRole'
      Path: /
      Policies:
        - PolicyName: ecs-describe
          PolicyDocument:
            Statement:
            - Effect: Allow
              Action:
              - ecs:DescribeClusters
              - ecs:DescribeServices
              Resource: "*"
        - PolicyName: ecs-update
          PolicyDocument:
            Statement:
            - Effect: Allow
              Action:
              - ecs:UpdateService
              Resource: !Ref MyService

  ServiceCountTaskDefinition:
    Type: 'AWS::ECS::TaskDefinition'
    Properties:
      NetworkMode: bridge
      Family: !Sub '${AWS::StackName}-service-count'
      ContainerDefinitions:
        - Name: 'service-count'
          Cpu: 10
          Essential: 'true'
          Image: 'jamessoubry/ecs-service-count:latest'
          Memory: 80
          Environment:
            - Name: SERVICE
              Value: !GetAtt MyService.Name
            # No need to provide these if you are running this on the same cluster as SERVICE 
            #- Name: CLUSTER
            #  Value: !Ref MyCluster
            #- Name: AWS_DEFAULT_REGION
            #  Value: !Ref AWS::Region


```