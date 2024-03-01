import streamlit as st
import time
import boto3
from app_config import AppConfig
from database_connection import DatabaseConnection
from llm_factory import LLMFactory
from qa_chain import QAChain
from langchain.prompts.prompt import PromptTemplate
from streamlit_cognito_auth import CognitoAuthenticator

import logging
logging.basicConfig(encoding='utf-8', level=logging.INFO)

# Set langchain debug mode
import langchain
langchain.debug = False

# Instantiate the necessary classes
app_config = AppConfig()

authenticator = CognitoAuthenticator(
    pool_id=app_config.get_cognito_pool_id(),
    app_client_id=app_config.get_cognito_app_client_id(),
    app_client_secret=app_config.get_cognito_app_client_secret(),
)

# Define functions

## initialize LLM QnA chain from Amazon Neptune knowledge graph
def init_qa_chain():
    # Load the LLM model
    llm_model = st.session_state["llm_model"]
    llm_factory = LLMFactory()
    llm = llm_factory.create_llm(llm_model)

    # Connect to the database
    neptune_host = st.session_state["neptune_host"]
    neptune_port = st.session_state["neptune_port"]
    db_connection = DatabaseConnection(neptune_host, neptune_port, use_https=True)
    graph = db_connection.connect()
    
    # Create the QA chain
    cypher_custom_template = st.session_state["cypher_custom_template"]
    custom_qa_template = st.session_state["custom_qa_template"]
    qa_prompt = PromptTemplate(input_variables=["context", "question"], template=custom_qa_template)
    cypher_prompt = PromptTemplate(input_variables=["schema", "question"], template=cypher_custom_template)
    qa_chain = QAChain(llm, graph, qa_prompt, cypher_prompt).create()
    return qa_chain
    
## parse response from the LLM query output
def get_query_response(qa_chain, prompt):
    try:
        output = qa_chain(prompt)
        intermediate_steps = output['intermediate_steps']
        logging.info(intermediate_steps)
        intermediate_steps_query = intermediate_steps[0]['query']
        query = intermediate_steps_query
        result = output['result']
        return {
            'query': query,
            'result': result
        }
    except Exception as e:
        st.chat_message("system").error(e)
        logging.error(e)
        return None

## build sidebar UI using streamlit 
def build_sidebar():
    with st.sidebar:
        st.text(f"Welcome, {authenticator.get_username()}")
        st.button("Logout", "logout_btn", on_click=logout)
            
        st.divider()

        model_list = ('anthropic.claude-v2',)
        st.selectbox("Pick the LLM", model_list, index=0, key="llm_model")
        st.divider()

        st.text_input("Neptune Host", key="neptune_host", value=app_config.get_neptune_host())
        st.text_input("Neptune Port", key="neptune_port", value=app_config.get_neptune_port())
        st.divider()
        st.checkbox("Display Generated Cypher?", key="display_generated_cypher", value=False)
        st.divider()
        st.text_area("Cypher Custom Prompt Template",key="cypher_custom_template", value=app_config.get_cypher_custom_template())
        st.text_area("QA Custom Prompt Template", key="custom_qa_template", value=app_config.get_custom_qa_template())
        st.divider()
        "[View the source code](https://github.com/aws-solutions-library-samples/guidance-for-digital-thread-using-graph-and-generative-ai-on-aws/)"


## build main UI using streamlit 
def build_ui():
    st.header("Ask your digital thread advisor 💬 🧠")
    with st.expander("MFG304-R | Building a knowledge graph and AI-powered manufacturing digital thread"):
        st.markdown(app_config.get_app_description())
    with st.expander('Example questions'):
        st.markdown(app_config.get_example_query())
    
    # initialize QA chain
    qa_chain = init_qa_chain()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What's up?"):
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner('Wait for it...'):
            response = get_query_response(qa_chain, prompt) 
        
        if st.session_state["display_generated_cypher"] is True:
            with st.chat_message("system"):
                message_placeholder = st.empty()
                msg = ""
                if response:
                    msg = " Generated Cypher:\n\n`" +   response['query']   +"`"
                    message_placeholder.markdown(msg)
                else:
                    msg = 'Oops..something went wrong. Please try another query.'
                    message_placeholder.error(msg)
                    st.stop()
            
        with st.chat_message("assistant"):
            output = response['result']
            message_placeholder = st.empty()
            full_response = ""

            # Simulate stream of response with milliseconds delay
            for chunk in output.split():
                full_response += chunk + " "
                time.sleep(0.02)
                # Add a blinking cursor to simulate typing
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "user", "content": prompt})
        # st.session_state.messages.append({"role": "system", "content": msg})
        st.session_state.messages.append({"role": "assistant", "content": full_response})

## login auth with cognito    
def login():
    is_logged_in = authenticator.login()
    #if not logged in, stop the app and keep in login page
    if not is_logged_in:
        st.stop()

## logout auth with cognito    
def logout():
    authenticator.logout()  

    # reset session variable and stop the app
    reset_session()
    st.stop()

    #redirect to login page
    login()
    
def reset_session():
    st.session_state["llm_model"] = "anthropic.claude-v2"
    st.session_state["neptune_host"] = app_config.get_neptune_host()
    st.session_state["neptune_port"] = app_config.get_neptune_port()
    st.session_state["cypher_custom_template"] = app_config.get_cypher_custom_template()
    st.session_state["custom_qa_template"] = app_config.get_custom_qa_template()
    st.session_state["display_generated_cypher"] = False
    st.session_state.messages = []
    
# Main application logic
if __name__ == "__main__":

    # Auth with cognito and redirect to login page if not logged in
    login()

    # Set a default session values
    if ("llm_model" not in st.session_state) or (not st.session_state["llm_model"]):
        st.session_state["llm_model"] = "anthropic.claude-v2"
    if ("neptune_host" not in st.session_state) or (not st.session_state["neptune_host"]):
        st.session_state["neptune_host"] = app_config.get_neptune_host()
    if ("neptune_port" not in st.session_state) or (not st.session_state["neptune_port"]):
        st.session_state["neptune_port"] = app_config.get_neptune_port()
    if ("cypher_custom_template" not in st.session_state) or (not st.session_state["cypher_custom_template"]):
        st.session_state["cypher_custom_template"] = app_config.get_cypher_custom_template()
    if ("custom_qa_template" not in st.session_state) or (not st.session_state["custom_qa_template"]):
        st.session_state["custom_qa_template"] = app_config.get_custom_qa_template()
    if ("display_generated_cypher" not in st.session_state) or (st.session_state["display_generated_cypher"] == ""):
        st.session_state["display_generated_cypher"] = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Build the User Interface
    build_sidebar()
    build_ui()

    
    

    
