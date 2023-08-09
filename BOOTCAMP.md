## AWS Account

* **Region**: eu-west-1
* **AWS Console Link**: https://812432071470.signin.aws.amazon.com/console
* **IAM Users**
    - BookingServiceUser1-5
    - LoyaltyServiceUser1-5
    - PaymentServiceUser1-5

## Checkpoints

This is a guideline for groups to understand where they should be at around this particular time.

### Day 1

* **Morning**
    - [x] Architectures, and agreement on integration patterns
    - [x] Everyone able to access their team's Cloud9 environment
* **Afternoon**
    - [x] Service partially implemented - one user story being testable via the front-end or API directly

### Day 2

* **Morning**
    - [x] Majority of teams having their service as MVP
    - [x] At least one team pushing changes through a pipeline
    - [x] Presenters to sit down for at least 30m to help those who might be late
* **Afternoon**
    - [x] At least Tracing being enabled
    - [x] Majority or all services integrated with the front-end


## Services

### Booking service

* “As a customer, I want to be able to book a flight for today or at a particular date” 
* “As a customer, I want to be able to see my previous booking”
* "As a customer, I would like to only be charged if my booking is confirmed"

**Tip**: Booking could communicate a successful transaction to Loyalty service to compute customer's points asynchronously. You may not need an User Registration service.

#### Front-end contract

**Booking data format expected by front-end**

```json
[
    {
        "id": "A1",
        "status": "CONFIRMED",
        "bookingReference": "Flkuc1",
        "departureCity": "London",
        "createdAt": "2019-01-01T08:00+0000",
        "outboundFlight": {
            "id": "173ec46b-0e12-45fe-9ba1-511abde3d318",
            "departureDate": "2019-01-16T08:00+0000",
            "departureAirportCode": "LGW",
            "departureAirportName": "London Gatwick",
            "departureCity": "London",
            "departureLocale": "Europe/London",
            "arrivalDate": "2019-01-16T10:15+0000",
            "arrivalAirportCode": "MAD",
            "arrivalAirportName": "Madrid Barajas",
            "arrivalCity": "Madrid",
            "arrivalLocale": "Europe/Madrid",
            "ticketPrice": 400,
            "ticketCurrency": "EUR",
            "flightNumber": 1812,
            "seatAllocation": 100
        },
        "inboundFlight": {
            ...
        }
    }
]
```

**Booking creation data sent by front-end**

```json
{
    "chargeToken": "stripe-pre-authorization-payment-token",
    "outboundFlight": "outbound-flight-id"
}
```

**Booking creation response expected by front-end**

```json
{
    "bookingId": "booking-unique-id"
}
```

---

### Catalog service

* "As a customer, I want to get a list of flights for a destination" 
* "As a customer, I want to fetch a flight by its unique ID"

#### Front-end contract

**Flight data format expected by front-end**

```json
[
    {
        "id": "173ec46b-0e12-45fe-9ba1-511abde3d318",
        "departureDate": "2019-01-16T08:00+0000",
        "departureAirportCode": "LGW",
        "departureAirportName": "London Gatwick",
        "departureCity": "London",
        "departureLocale": "Europe/London",
        "arrivalDate": "2019-01-16T10:15+0000",
        "arrivalAirportCode": "MAD",
        "arrivalAirportName": "Madrid Barajas",
        "arrivalCity": "Madrid",
        "arrivalLocale": "Europe/Madrid",
        "ticketPrice": 400,
        "ticketCurrency": "EUR",
        "flightNumber": 1812
    }
]
```

---

### Loyalty service

* "As a customer, I want to earn loyalty points upon successful bookings"
* "As a customer, I would like to know how far I am to the next tier"

#### Front-end contract

**Loyalty data format expected by front-end**

```json
{
      "points": 400,
      "level": "bronze",
      "remainingPoints":49600
}
```

---

### Payment service

* "As a customer, I want to an authorization for my flight not the full amount"
* "As a customer, I'd like to pay for the full amount once my booking is confirmed"
* "As a customer, I'd like to ask for a refund for previous payments"

#### Front-end contract

**Pre-authorization payment data sent by front-end**

```json
{
    "amount": 100,
    "currency": "EUR",
    "description": "Payment by lessa@amazon.co.uk",
    "email": "lessa@amazon.co.uk",
    "stripeToken: "tok_1FGitIF4aIiftV70RnarbaYH"
}
```

**Pre-authorization data format expected by front-end**

```json
{
    "createdCharge": {
        ...stripe charge object
        https://stripe.com/docs/api/charges/object
    }
}
```

---

## Resources

### HOWTO

* [Deploying a hello world using SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started-hello-world.html)
* [Creating a back-end using Amplify](https://aws-amplify.github.io/docs/js/start#step-2-set-up-your-backend)

### Snippets

**Using a docker container for SAM Build**

```bash
sam build --use-container
```

**Package and deploy to CloudFormation**

```bash
    sam package \
    --s3-bucket S3_BUCKET \
    --output-template-file packaged.yaml
```

**Change Stack Name to something unique to you**

```bash
    sam deploy \
    --template-file packaged.yaml \
    --stack-name <CFN Stack Name> \
    --capabilities CAPABILITY_IAM
```

**Find out the API Gateway URL to execute**

```bash
aws cloudformation describe-stacks --stack-name <CFN Stack Name> --query 'Stacks[].Outputs'
```

**Tail Function logs live**

```bash
sam logs \
    --stack-name <CFN Stack Name> \
    -n HelloWorldFunction -t
```

**Generate a fake payload**

* ``sam local generate-event apigateway aws-proxy``**
* ``sam local generate-event apigateway aws-proxy | sam local invoke HelloWorldFunction``

**Translate SAM template to standard CloudFormation template**

1. Translate SAM to Cloudformation by validating a template: `sam validate --debug 2> debug.yaml`
2. Open `debug.yaml` and search for `Resources:`

**Validating/Linting a SAM or CloudFormation template**

```bash
cfn-lint template.yaml
```

---


### Cheatsheet

#### Lambda and DynamoDB with secondary index

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

  #
  # Catalog table has `id` as primary key
  # A Secondary index named `ByLoyaltyStatus`
  # it allows clients to query by `customerId` and `level` attributes
  #
  LoyaltyDataTable:
    Type: AWS::DynamoDB::Table
    Properties:
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: customerId
          AttributeType: S
        - AttributeName: level
          AttributeType: S
        - AttributeName: id
          AttributeType: S
      KeySchema:
        - AttributeName: id
          KeyType: HASH
      GlobalSecondaryIndexes:
        - IndexName: ByLoyaltyStatus
          KeySchema:
            - AttributeName: customerId
              KeyType: HASH
            - AttributeName: level
              KeyType: RANGE
          Projection:
              ProjectionType: ALL
      SSESpecification:
        SSEEnabled:  yes

  IngestFunc:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ingest
      Handler: index.handler
      Runtime: nodejs8.10
      #
      # Provides CRUD permission to a DynamoDB table
      #
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref LoyaltyDataTable
      Environment:
        Variables:
          TABLE_NAME: !Ref LoyaltyDataTable
```


#### API Gateway CORS and Cognito Authorization

```yaml
Globals:
  Api:
    Cors:
      AllowMethods: "'OPTIONS,POST,GET'"
      AllowHeaders: "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
      AllowOrigin: "'*'"
    Auth:
      Authorizers:
          CognitoAuth:
            UserPoolArn: "arn:aws:cognito-idp:eu-west-1:812432071470:userpool/eu-west-1_EnZRa5skP"

### --- Function using Cognito Auth ---
  RetrieveBookings:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: bookings
      Handler: retrieve.lambdaHandler
      Runtime: nodejs10.x
      Environment:
        Variables:
          TABLE_NAME: !Ref BookingTable
      Policies:
        - AWSLambdaBasicExecutionRole
        - AmazonDynamoDBReadOnlyAccess
      Events:
        RetrieveBookingsAPICall:
          Type: Api
          Properties:
            Path: /bookings
            Method: GET
            Auth:
              Authorizer: CognitoAuth
              
### --- Function returning CORS headers ---
# ...
    # return {
    #     ...
    #     headers: {
    #         "Access-Control-Allow-Origin": "*",
    #         "Access-Control-Allow-Headers": "Content-Type",
    #         "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    #     }
    # }
```

#### API Gateway and Lambda X-Ray Tracing

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Tracing: Active
  Api:
    TracingEnabled: true
```


#### Stripe integration API using SAR

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31

Parameters:
    StripeKey:
        Type: String
        Description: Stripe Secret Key for SAR App

Resources:

  StripePaymentApplicationKeyParameter:
    Type: "AWS::SSM::Parameter"
    Properties:
        Name: /service/payment/stripe-secret-key
        Description: Stripe Key for SAR App
        Type: String
        Value: !Ref StripeKey

  StripePaymentApplication:
    DependsOn: StripePaymentApplicationKeyParameter
    Type: AWS::Serverless::Application
    Properties:
      Location:
        ApplicationId: arn:aws:serverlessrepo:us-east-1:375983427419:applications/api-lambda-stripe-charge
        SemanticVersion: 4.4.0
      Parameters:
        EnableInstantCapture: "false"
        SSMParameterPath: service/payment/stripe-secret-key

# 
# Example function to collect payment via the Stripe API
#
  # CollectPayment:
  #   Type: AWS::Serverless::Function
  #   Properties:
  #     FunctionName: !Sub Airline-CollectPayment-${Stage}
  #     Handler: collect.lambda_handler
  #     Runtime: python3.7
  #     CodeUri: src/collect-payment
  #     Timeout: 10
  #     Environment:
  #       Variables:
  #         PAYMENT_API_URL: !GetAtt StripePaymentApplication.Outputs.CaptureApiUrl


Outputs:
  PaymentCaptureUrl:
    Value: !Sub ${StripePaymentApplication.Outputs.CaptureApiUrl}
    Description: Payment Endpoint for capturing payments (collect pre-authorization payment)

  PaymentChargeUrl:
    Value: !Sub ${StripePaymentApplication.Outputs.ChargeApiUrl}
    Description: Payment Endpoint for collecting payments (pre-authorize payment)

  RefundApiUrl:
    Value: !Sub ${StripePaymentApplication.Outputs.RefundApiUrl}
    Description: Payment Endpoint for refunding payments
```

#### API Gateway plus State Machine integration

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: API Gateway integration with Step Functions demo w/ inline Swagger

Resources:


  #####################
  #  IAM Service Role #
  #####################

      StepFunctionsServiceRole:
          Type: "AWS::IAM::Role"
          Properties:
              Path: "/"
              ManagedPolicyArns:
                - "arn:aws:iam::aws:policy/AWSStepFunctionsFullAccess"
              AssumeRolePolicyDocument:
                Version: "2012-10-17"
                Statement:
                  -
                    Sid: "AllowStepFunctionsServiceToAssumeRole"
                    Effect: "Allow"
                    Action: 
                      - "sts:AssumeRole"
                    Principal:
                      Service:
                        - !Sub "states.${AWS::Region}.amazonaws.com"
              Policies:
                -
                  PolicyName: "CallLambdaFunctions"
                  PolicyDocument:
                    Version: '2012-10-17'
                    Statement:
                      -
                        Effect: "Allow"
                        Action:
                          - "lambda:InvokeFunction"
                        Resource: '*' # You can limit this to functions defined within this template later

      # IAM Role API Gateway will assume in order to call StepFunctions StartExecution API
      ApiGatewayStepFunctionsRole:
        Type: "AWS::IAM::Role"
        Properties:
            Path: "/"
            AssumeRolePolicyDocument:
              Version: "2012-10-17"
              Statement:
                -
                  Sid: "AllowApiGatewayServiceToAssumeRole"
                  Effect: "Allow"
                  Action: 
                    - "sts:AssumeRole"
                  Principal:
                    Service:
                      - "apigateway.amazonaws.com"
            Policies:
              -
                PolicyName: "CallStepFunctions"
                PolicyDocument:
                  Version: '2012-10-17'
                  Statement:
                    -
                      Effect: "Allow"
                      Action:
                        - "states:StartExecution"
                      Resource: 
                        - !Ref StepFunctionStateMachine

  #################################
  #  Step Functions State Machine #
  #################################

      StepFunctionStateMachine:
        Type: "AWS::StepFunctions::StateMachine"
        Properties:
          DefinitionString: !Sub |
            {
                "Comment": "Inline Step Functions",
                "StartAt": "Hello",
                "States": {
                  "Hello": {
                    "Type" : "Pass",
                    "Next": "SayBye"
                  },
                  "SayBye": {
                    "Type": "Pass",
                    "End": true
                  }
                }
            }
          RoleArn: !GetAtt StepFunctionsServiceRole.Arn

  #########################
  # API GW Inline Swagger #
  #########################

      StepFunctionsAPI:
        Type: AWS::Serverless::Api
        Properties:
            StageName: dev
            DefinitionBody:
                swagger: 2.0
                info:
                  title:
                    Ref: AWS::StackName
                paths:
                  "/pay":
                    post:
                      responses:
                        "200":
                          description: "200 response"
                      x-amazon-apigateway-integration:
                        credentials: !GetAtt ApiGatewayStepFunctionsRole.Arn
                        responses:
                          default:
                            statusCode: "200"
                        requestTemplates:
                          application/json: !Sub |
                            {
                              "input": "$util.escapeJavaScript($input.json('$'))",
                              "name": "$context.requestId",
                              "stateMachineArn": "${StepFunctionStateMachine}"
                            }
                        uri: !Sub "arn:aws:apigateway:${AWS::Region}:states:action/StartExecution"
                        passthroughBehavior: "when_no_match"
                        httpMethod: "POST"
                        type: "aws"

Outputs:

        WorkflowApi:
          Description: Workflow URL 
          Value: !Sub "https://${StepFunctionsAPI}.execute-api.${AWS::Region}.amazonaws.com/dev/workflow"

        StepFunctionsStateMachine:
          Description: Step Functions State Machine ARN
          Value: !Ref StepFunctionStateMachine
```


---

#### API Gateway -> NLB -> VPC

This also shows how to do inline Swagger with API GW + Lambda.

```yaml
AWSTemplateFormatVersion: 2010-09-09
Transform: AWS::Serverless-2016-10-31

Parameters:
 
  InternalNetworkLoadBalancerUri:
    Type: String
    Default: http://awseb-AWSEB-144KLGDV95UQ3-85ffedf6feb05936.elb.ap-southeast-2.amazonaws.com

  # OR you could create a new NLB ;)
  InternalNetworkLoadBalancerArn:
    Type: String
    Default: arn:aws:elasticloadbalancing:ap-southeast-2:853843566408:loadbalancer/net/awseb-AWSEB-144KLGDV95UQ3/85ffedf6feb05936

Resources:

  NbnVPCLink:
    Type: "AWS::ApiGateway::VpcLink"
    Properties:
      Description: NBN Demo Vpc Link
      Name: nbn-demo-vpc-link
      TargetArns:
        - !Ref InternalNetworkLoadBalancerArn

#
# API Gateway Inline Swagger definition
#

  DemoApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: Prod
      EndpointConfiguration: REGIONAL
      DefinitionBody:
        swagger: "2.0"
        info:
          version: "1.0"
          title: "api-demo"
        basePath: "/Prod"
        schemes:
        - "https"
        paths:
          /:
            get:
              responses:
                '200':
                  description: "Successful operation"
              x-amazon-apigateway-integration:
                uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${HelloWorld.Arn}/invocations'
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                type: "aws_proxy"
            post:
              responses:
                '200':
                  description: "successful operation"
                '400':
                  description: "Invalid operation"
                '404':
                  description: "Not found"
              x-amazon-apigateway-integration:
                uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${HelloWorld.Arn}/invocations'
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                type: "aws_proxy"
          /customer:
            get:
              responses: {}
              x-amazon-apigateway-integration:
                uri: !Sub 'arn:aws:apigateway:${AWS::Region}:lambda:path/2015-03-31/functions/${CustomerFunction.Arn}/invocations'
                passthroughBehavior: "when_no_match"
                httpMethod: "POST"
                type: "aws_proxy"
          # Setups Private Integration via VPC Link (API GW -> NLB)
          /internal:
            get:
              produces:
              - "application/json"
              responses:
                '200':
                  description: "Successful operation"
              x-amazon-apigateway-integration:
                responses:
                  default:
                    statusCode: "200"
                uri: !Ref InternalNetworkLoadBalancerUri
                passthroughBehavior: "when_no_match"
                connectionType: "VPC_LINK"
                connectionId: !Ref NbnVPCLink
                httpMethod: "GET"
                type: "http"


  HelloWorld:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: python3.6
      Events:
        GetEvent:
          Type: Api
          Properties:
            Path: /
            Method: get
            RestApiId: !Ref DemoApi   ### This will add API GW permission to call this function on this path 
        PostEvent:
          Type: Api
          Properties:
            Path: /
            Method: post
            RestApiId: !Ref DemoApi

  CustomerFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: customer_function.handler
      Runtime: python3.6
      Events:
        GetEvent:
          Type: Api
          Properties:
            Path: /customer
            Method: get
            RestApiId: !Ref DemoApi
```

---

### Further reading

* [API Gateway -> Step Functions template](http://bit.ly/notifications_workflow)
    * Templates are under `cloudformation/snippets` folder
* [Developer Laptop + Simple Crypto Svc code](http://bit.ly/initiate-serverless)
* [Python DynamoDB CRUD Tutorial](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html)
* **Books**
    - [Domain Driven Design (2003)](https://www.amazon.co.uk/Domain-Driven-Design-Tackling-Complexity-Software/dp/0321125215/ref=sr_1_1)
    - [Building Microservices (2015)](https://www.amazon.co.uk/Building-Microservices-Sam-Newman/dp/1491950358/ref=pd_bxgy_14_img_3)
    - [Release It (2018)](https://www.amazon.com/Release-Design-Deploy-Production-Ready-Software/dp/1680502395/ref=dp_ob_title_bk)
    - [DevOps Handbook](https://www.amazon.co.uk/Devops-Handbook-World-Class-Reliability-Organizations/dp/1942788002/ref=sr_1_1)
    - [Serverless Applications with Node.js](https://www.manning.com/books/serverless-applications-with-node-js)
