# ecs-service-count
Docker container to adjust ECS service count to follow cluster instance count

Docker execution example:
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
            - Name: CLUSTER
              Value: !Ref MyCluster


```