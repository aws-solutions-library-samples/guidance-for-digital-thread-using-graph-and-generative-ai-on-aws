#!/bin/bash

echo "This script is to clean up the demo application."

# confirm by input y
read -p "Are you sure to delete the demo application? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "Aborting."
    exit 1
fi

## clean up application
copilot app delete

rm -rf copilot/environments/demo

# delete cloudformation stack
NEPTUNE_STACK_NAME=mfg-dt-neptune
COGNITO_STACK_NAME=mfg-dt-cognito
IAM_STACK_NAME=mfg-dt-iam

IS_STACK_EXIST=false

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $NEPTUNE_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "Stack $NEPTUNE_STACK_NAME exists."
    aws cloudformation delete-stack --stack-name $NEPTUNE_STACK_NAME
    echo "CloudFormation Stack $NEPTUNE_STACK_NAME is being deleted. It will be removed in minutes."
fi

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $COGNITO_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "Stack $COGNITO_STACK_NAME exists."
    aws cloudformation delete-stack --stack-name $COGNITO_STACK_NAME
    echo "CloudFormation Stack $COGNITO_STACK_NAME is being deleted. It will be removed in minutes."
fi

# Check if the CloudFormation stack exists
stack_info=$(aws cloudformation describe-stacks --stack-name $IAM_STACK_NAME 2>&1)
# Check if the command was successful
if [ $? -eq 0 ]; then
    IS_STACK_EXIST=true
    echo "Stack $IAM_STACK_NAME exists."
    aws cloudformation delete-stack --stack-name $IAM_STACK_NAME
    echo "CloudFormation Stack $IAM_STACK_NAME is being deleted. It will be removed in minutes."
fi

if [ $IS_STACK_EXIST = true ]; then
    echo "CloudFormation is being deleted. It will be removed in minutes. Please check in the CloudFormation console https://console.aws.amazon.com/cloudformation/home"
fi

exit 0

