#!/bin/bash

echo "This script is to clean up the Manufacturing Digital thread (Graph and Generative AI) demo application."

# confirm by input y
read -p "Are you sure to delete the demo application? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborted...."
    exit 1
fi

## clean up application
echo "Manufacturing Digital Thread aws copilot application will be deleted. Delete started..."
copilot app delete
rm -rf copilot/environments/demo

# Revert app.env files to empty using cat
cat <<EOF > copilot/genai-chatbot-app/app.env
NEPTUNE_HOST=
NEPTUNE_PORT=
COGNITO_POOL_ID=
COGNITO_APP_CLIENT_ID=
COGNITO_APP_CLIENT_SECRET=
EOF

echo "Manufacturing Digital Thread aws copilot application deleted successfully!!!!"

# delete CloudFormation stack
NEPTUNE_STACK_NAME=mfg-dt-neptune
COGNITO_STACK_NAME=mfg-dt-cognito
IAM_STACK_NAME=mfg-dt-iam

IS_STACK_EXIST=false

echo "CloudFormation delete stack started..."

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $NEPTUNE_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "Neptune Stack $NEPTUNE_STACK_NAME exists. Neptune resources will be deleted. Delete stack started..."
    aws cloudformation delete-stack --stack-name $NEPTUNE_STACK_NAME
    echo "CloudFormation Neptune Stack $NEPTUNE_STACK_NAME is being deleted. It will be removed in minutes."
fi

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $COGNITO_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "Cognito Stack $COGNITO_STACK_NAME exists. Delete stack started..."
    aws cloudformation delete-stack --stack-name $COGNITO_STACK_NAME
    echo "CloudFormation Cognito Stack $COGNITO_STACK_NAME is being deleted. It will be removed in minutes."
fi

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $IAM_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "IAM Stack $IAM_STACK_NAME exists. Delete stack started..."
    aws cloudformation delete-stack --stack-name $IAM_STACK_NAME
    echo "CloudFormation IAM Stack $IAM_STACK_NAME is being deleted. It will be removed in minutes."
fi

if [ $IS_STACK_EXIST = true ]; then
    echo "CloudFormation is being deleted. It will be removed in minutes. Please check the CloudFormation console https://console.aws.amazon.com/cloudformation/home"
fi

exit 0

