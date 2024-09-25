import streamlit as st
import boto3
from app_config import AppConfig
# from langchain_community.llms import Bedrock
from langchain_aws import ChatBedrock

class LLMFactory:
    def __init__(self):
        # Setup bedrock 
        self.bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
    ) 
        

    def create_llm(self, llm_model):
        inference_modifier = {"temperature": 0.01}
        # inference_modifier = {"temperature": 0.01,
        #                     "top_k": 250,
        #                     "top_p": 1,
        #                     "stop_sequences": ["\n\nHuman"]}
    
        model_list = AppConfig().get_model_list()

        if llm_model == 'Claude 2.1':
            model_id = 'anthropic.claude-v2:1'
        elif llm_model == 'Claude 3 Sonnet':
            model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        elif llm_model == 'Claude 3.5 Sonnet':
            model_id = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
        elif llm_model == 'Llama 3 70b Instruct':
            model_id = 'meta.llama3-70b-instruct-v1:0'
        elif llm_model == 'Mistral Large':
            model_id = 'mistral.mistral-large-2402-v1:0'
        else:
            model_id = ''

        model_id_list = ('anthropic.claude-v2',
                      'anthropic.claude-v2:1',
                      'anthropic.claude-3-haiku-20240307-v1:0', 
                      'anthropic.claude-3-sonnet-20240229-v1:0',
                      'anthropic.claude-3-5-sonnet-20240620-v1:0',
                      'meta.llama3-8b-instruct-v1:0',
                      'meta.llama3-70b-instruct-v1:0',
                      'mistral.mistral-large-2402-v1:0',
                      'mistral.mixtral-8x7b-instruct-v0:1'
                      )
        if model_id in model_id_list:
            llm = ChatBedrock(model_id=model_id,
                          client=self.bedrock_runtime, 
                          model_kwargs=inference_modifier)
        else:
            st.error('LLM not supported yet')
            st.stop()
            llm = None
        return llm