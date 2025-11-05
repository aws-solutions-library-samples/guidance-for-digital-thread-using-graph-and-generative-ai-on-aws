#!/bin/bash

echo "This script is to deploy the Manufacturing Digital thread (Graph and Generative AI) application."
# check if AWS_DEFAULT_REGION exist in env
if [ -z "$AWS_DEFAULT_REGION" ]; then
  echo "Aborted....AWS_DEFAULT_REGION is not set!!!!"
  echo "> export AWS_DEFAULT_REGION=xx-xxxx-xx"
  exit 1
fi
echo ""
echo "The application will be deployed in $AWS_DEFAULT_REGION region...."

echo "Checking AWS credentials...."
stack_info=$(aws cloudformation list-stacks 2>&1)
# $? not eq 0
if [ $? -ne 0 ]; then
  echo ""
  echo "Aborted....Please check your AWS credentials!!!!"
  exit 1
fi

echo ""
echo "AWS credentials verified successfully!!!"
echo ""
echo "Checking docker daemon is running..."
if (! docker stats --no-stream ); then
  echo ""
  echo "Aborted....Please check whether docker daemon is running!!!!"
  exit 1
fi
echo ""
echo "docker daemon is running!!!"

ACCOUNT_ID=$(aws sts get-caller-identity --output text --query Account)
PROJECT_TAG="Key=Project,Value=mfg-digitalthread"

# Step 1: Create Cognito User Pool for MFG DigitalThread
echo ""
echo "Step 1: Create Cognito User Pool for Manufacturing Digital Thread: Started!!!!"

COGNITO_STACK_NAME=mfg-dt-cognito
COGNITO_DOMAIN_NAME=mfg-dt-$ACCOUNT_ID
echo ""
echo "Checking whether Cognito User Pool stack $COGNITO_STACK_NAME already exists...."
# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $COGNITO_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Cognito User Pool stack $COGNITO_STACK_NAME already exists. Skipping Cognito User pool creation process..."
else
  echo ""
  echo "Cognito User Pool stack $COGNITO_STACK_NAME doesnot exist. $COGNITO_STACK_NAME is creating...(Takes 5 min)"
  aws cloudformation create-stack \
    --stack-name $COGNITO_STACK_NAME \
    --template-body file://$(pwd)/src/cfn-template/cognito.yml \
    --parameters ParameterKey=CognitoDomain,ParameterValue=$COGNITO_DOMAIN_NAME \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --tags $PROJECT_TAG
fi

aws cloudformation wait stack-create-complete --stack-name $COGNITO_STACK_NAME
if [ $? -ne 0 ]; then
  echo ""
  echo "Aborted...Cognito User Pool stack $COGNITO_STACK_NAME creation failed. please check the errors in the AWS Cloudformation console!!!!"
  exit $?
fi

outputs=$(aws cloudformation describe-stacks --stack-name $COGNITO_STACK_NAME --query "Stacks[0].Outputs") 
CognitoUserPoolID=$(echo $outputs | jq -r '.[] | select(.OutputKey=="CognitoUserPoolID") | .OutputValue')
CognitoAppClientSecret=$(echo $outputs | jq -r '.[] | select(.OutputKey=="CognitoAppClientSecret") | .OutputValue')
CognitoAppClientID=$(echo $outputs | jq -r '.[] | select(.OutputKey=="CognitoAppClientID") | .OutputValue')


echo """$COGNITO_STACK_NAME Output:
CognitoUserPoolID=$CognitoUserPoolID
CognitoAppClientSecret=$CognitoAppClientSecret
CognitoAppClientID=$CognitoAppClientID"""

echo ""
echo "Cognito User Pool stack $COGNITO_STACK_NAME created successfully!!!!"

## create demo user
DEMO_USERNAME=demo_user
DEMO_USER_EMAIL=demo.user@example.com
DEMO_USER_PW='TempPassw0rd!'
# Get the list of users with the specified username
response=$(aws cognito-idp list-users --user-pool-id $CognitoUserPoolID --filter "username=\"$DEMO_USERNAME\"")
echo ""
echo "Creating demo user $DEMO_USERNAME in the user pool...."

# Check if the Users array in the response is empty
if [[ $response == *"Username"* ]]; then
  echo ""
  echo "User $DEMO_USERNAME already exists in the user pool. Skipping demo user creation process..."
else
  aws cognito-idp admin-create-user \
    --user-pool-id $CognitoUserPoolID \
    --username $DEMO_USERNAME \
    --user-attributes Name=name,Value=DemoUser Name=email,Value=$DEMO_USER_EMAIL Name=email_verified,Value=true \
    --temporary-password $DEMO_USER_PW \
    --message-action SUPPRESS \
    --desired-delivery-mediums EMAIL \
    --output text
  echo ""
  echo "Demo user $DEMO_USERNAME created successfully."
fi

echo ""
echo "Step 1: Create Cognito User Pool for Manufacturing Digital Thread: Completed!!!!!"

# Step 2: Create Amazon Netpune for MFG DigitalThread
echo ""
echo "Step 2: Create Amazon Netpune for Manufacturing Digital Thread: Started....."

NEPTUNE_STACK_NAME=mfg-dt-neptune
echo ""
echo "Checking whether Neptune stack $NEPTUNE_STACK_NAME already exists...."

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $NEPTUNE_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
  echo ""
  echo "Neptune stack $NEPTUNE_STACK_NAME already exists. Skipping neptune cluster creation processs... "
else
  echo ""
  echo "Neptune stack $NEPTUNE_STACK_NAME is creating.... (Takes 30 min)"
  aws cloudformation create-stack \
    --stack-name $NEPTUNE_STACK_NAME \
    --template-body file://$(pwd)/src/cfn-template/neptune-full-stack-nested-template.json \
    --parameters ParameterKey=DBClusterId,ParameterValue="" ParameterKey=NotebookInstanceType,ParameterValue=ml.t3.medium ParameterKey=SetupGremlinConsole,ParameterValue=true ParameterKey=SetupRDF4JConsole,ParameterValue=true \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
    --tags $PROJECT_TAG
fi

aws cloudformation wait stack-create-complete --stack-name $NEPTUNE_STACK_NAME
if [ $? -ne 0 ]; then
  echo ""
  echo "Aborted...Neptune stack $NEPTUNE_STACK_NAME creation failed. please check the errors in the AWS Cloudformation console.. "
  exit $?
fi


outputs=$(aws cloudformation describe-stacks --stack-name $NEPTUNE_STACK_NAME --query "Stacks[0].Outputs") 
DBClusterId=$(echo $outputs | jq -r '.[] | select(.OutputKey=="DBClusterId") | .OutputValue')
DBClusterPort=$(echo $outputs | jq -r '.[] | select(.OutputKey=="DBClusterPort") | .OutputValue')
DBClusterEndpoint=$(echo $outputs | jq -r '.[] | select(.OutputKey=="DBClusterEndpoint") | .OutputValue')
DBClusterReadEndpoint=$(echo $outputs | jq -r '.[] | select(.OutputKey=="DBClusterReadEndpoint") | .OutputValue')
LoaderEndpoint=$(echo $outputs | jq -r '.[] | select(.OutputKey=="LoaderEndpoint") | .OutputValue')
NeptuneLoadFromS3IAMRoleArn=$(echo $outputs | jq -r '.[] | select(.OutputKey=="NeptuneLoadFromS3IAMRoleArn") | .OutputValue')
NeptuneSagemakerNotebook=$(echo $outputs | jq -r '.[] | select(.OutputKey=="NeptuneSagemakerNotebook") | .OutputValue')
VPC=$(echo $outputs | jq -r '.[] | select(.OutputKey=="VPC") | .OutputValue')
PrivateSubnet1=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PrivateSubnet1") | .OutputValue')
PrivateSubnet2=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PrivateSubnet2") | .OutputValue')
PrivateSubnet3=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PrivateSubnet3") | .OutputValue')
PublicSubnet1=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PublicSubnet1") | .OutputValue')
PublicSubnet2=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PublicSubnet2") | .OutputValue')
PublicSubnet3=$(echo $outputs | jq -r '.[] | select(.OutputKey=="PublicSubnet3") | .OutputValue')

echo ""
echo """$NEPTUNE_STACK_NAME Output:
DBClusterId=$DBClusterId
DBClusterPort=$DBClusterPort
DBClusterEndpoint=$DBClusterEndpoint
DBClusterReadEndpoint=$DBClusterReadEndpoint
LoaderEndpoint=$LoaderEndpoint
NeptuneLoadFromS3IAMRoleArn=$NeptuneLoadFromS3IAMRoleArn
NeptuneSagemakerNotebook=$NeptuneSagemakerNotebook
VPC=$VPC
PublicSubnet1=$PublicSubnet1
PublicSubnet2=$PublicSubnet2
PublicSubnet3=$PublicSubnet3
PrivateSubnet1=$PrivateSubnet1
PrivateSubnet2=$PrivateSubnet2
PrivateSubnet3=$PrivateSubnet3
"""
echo ""
echo "Neptune stack $NEPTUNE_STACK_NAME created successfully!!!!"
echo ""
echo "Step 2: Create Amazon Netpune for Manufacturing Digital Thread: Completed!!!!"


# Step 3: Init app with AWS copilot
echo ""
echo "Step 3: Init Manufacturing Digital Thread application with AWS copilot: Started...."
## setup env variable which are used in the manifest
export NEPTUNE_HOST=$DBClusterEndpoint
export NEPTUNE_PORT=$DBClusterPort
export COGNITO_POOL_ID=$CognitoUserPoolID
export COGNITO_APP_CLIENT_ID=$CognitoAppClientID
export COGNITO_APP_CLIENT_SECRET=$CognitoAppClientSecret

# write env variable to an .env file using cat
cat <<EOF > copilot/genai-chatbot-app/app.env
NEPTUNE_HOST=${DBClusterEndpoint}
NEPTUNE_PORT=${DBClusterPort}
COGNITO_POOL_ID=${CognitoUserPoolID}
COGNITO_APP_CLIENT_ID=${CognitoAppClientID}
COGNITO_APP_CLIENT_SECRET=${CognitoAppClientSecret}
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION}
EOF

## init app with AWS 
copilot app init genai-chatbot-app

## create env with AWS
copilot env init \
  --name demo \
  --import-vpc-id $VPC \
  --import-public-subnets $PublicSubnet1,$PublicSubnet2,$PublicSubnet3 \
  --import-private-subnets $PrivateSubnet1,$PrivateSubnet2,$PrivateSubnet3 \
  --region $AWS_DEFAULT_REGION

echo ""
echo "Step 3: Init Manufacturing Digital Thread application with AWS copilot: Completed!!!!"

## Step 4: Deploy app with AWS copilot
echo ""
echo "Step 4: Deploy Manufacturing Digital Thread application with AWS copilot: Started...."

## deploy env
copilot env deploy --name demo

## deploy service 
copilot deploy

echo ""
echo "Step 4: Deploy Manufacturing Digital Thread application with AWS copilot: Completed!!!"
echo ""
echo "Manufacturing Digital thread (Graph and Generative AI) application deployed successfully!!!!"

exit 0