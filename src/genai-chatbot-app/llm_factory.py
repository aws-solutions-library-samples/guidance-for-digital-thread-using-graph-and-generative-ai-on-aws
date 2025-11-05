import streamlit as st
import boto3
from app_config import AppConfig

from langchain_aws import ChatBedrockConverse

class LLMFactory:
    def __init__(self):
        # Setup bedrock 
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
        ) 
        self.bedrock = boto3.client('bedrock')
        

    def create_llm(self, llm_model):
    
        if llm_model == 'Claude Sonnet 4':
            model_id = 'us.anthropic.claude-sonnet-4-20250514-v1:0'
        elif llm_model == 'Claude Sonnet 4.5':
            model_id = 'us.anthropic.claude-sonnet-4-5-20250929-v1:0'
        elif llm_model == 'Nova Pro':
            model_id = 'us.amazon.nova-pro-v1:0'
        else:
            llm_model = 'Claude Sonnet 4'
            model_id = 'us.anthropic.claude-sonnet-4-20250514-v1:0'


        llm = ChatBedrockConverse(model_id=model_id,
                        # client=self.bedrock_runtime, 
                        temperature=0)

        return llm