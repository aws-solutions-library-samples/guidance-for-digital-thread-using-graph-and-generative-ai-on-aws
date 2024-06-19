import streamlit as st
import boto3
# from langchain_community.llms import Bedrock
from langchain_aws import ChatBedrock

class LLMFactory:
    def __init__(self):
        # Setup bedrock (assume you have enabled anthropic.claude-v2 in Amazon Bedrock at the region)
        self.bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
    ) 

    def create_llm(self, llm_model):
        if llm_model == 'anthropic.claude-v2.1':
            inference_modifier = {'max_tokens_to_sample': 4096, 
                                  "temperature": 0.01,
                                  "top_k": 250,
                                  "top_p": 1,
                                  "stop_sequences": ["\n\nHuman"]}
            llm = ChatBedrock(model_id="anthropic.claude-v2.1",
                          client=self.bedrock_runtime, 
                          model_kwargs=inference_modifier)
        elif llm_model == 'anthropic.claude-3-haiku-20240307-v1:0':
            inference_modifier = {'max_tokens_to_sample': 4096, 
                                  "temperature": 0.01,
                                  "top_k": 250,
                                  "top_p": 1,
                                  "stop_sequences": ["\n\nHuman"]}
            llm = ChatBedrock(model_id="anthropic.claude-3-haiku-20240307-v1:0",
                          client=self.bedrock_runtime, 
                          model_kwargs=inference_modifier)
        
        else:
            st.error('LLM not supported yet')
            st.stop()
            llm = None
        return llm