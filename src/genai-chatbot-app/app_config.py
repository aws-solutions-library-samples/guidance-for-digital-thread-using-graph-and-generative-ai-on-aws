import os

class AppConfig:
    ## Variables ##
    NEPTUNE_HOST= os.getenv('NEPTUNE_HOST')
    NEPTUNE_PORT= os.getenv('NEPTUNE_PORT')

    cognito_pool_id = os.environ.get("COGNITO_POOL_ID")
    cognito_app_client_id = os.environ.get("COGNITO_APP_CLIENT_ID")
    cognito_app_client_secret = os.environ.get("COGNITO_APP_CLIENT_SECRET")
    
    CYPHER_CUSTOM_TEMPLATE = """<Instructions>
Generate the query in openCypher format and follow these rules:
1. Use undirected relationship for MATCH query.
2. Do not use `NONE`, `ALL` or `ANY` predicate functions, rather use list comprehensions.
3. Do not use `REDUCE` function. Rather use a combination of list comprehension and the `UNWIND` clause to achieve similar results.
4. Do not use `FOREACH` clause. Rather use a combination of `WITH` and `UNWIND` clauses to achieve similar results.
5. Use only the provided relationship types and properties in the schema.
6. Do not use any other relationship types or properties that are not provided.
7. Do not use new line.
</Instructions>

<schema>
{schema}
<schema>

<example>
question: can Emily access the project Turbo-Project?
cypher: MATCH (p:Project {{name: 'Turbo-Project'}})-[r:team_member]->(e:Employee {{name: 'Emily'}}) RETURN r.access
</example>
<example>
question: can Thomas access the project Turbo-Project?
cypher: MATCH (p:Project {{name: 'Turbo-Project'}})-[r:team_member]->(e:Employee {{name: 'Thomas'}})RETURN r.access
</example>
<example>
question: can you list the requirement, part and documents associated with the defect QC-1234-1?
cypher: MATCH (qc:QualityDefect {{name: "QC-1234-1"}})<-[:quality_defect]-(op:Operation)<-[:operation]-(po:ProductionOrder)<-[:production_order]-(part:Part)-[:specification|allocation_by_requirements]->(node) WHERE ((node:Requirement AND toLower(node.description) CONTAINS "rpm") OR (node:Document AND toLower(node.name) CONTAINS "cad")) RETURN node.name AS node_name,nCASE WHEN node:Requirement THEN node.description END AS req_desc, CASE WHEN node:Requirement THEN node.name END AS req_name, CASE WHEN node:Document THEN node.name END AS doc_name, CASE WHEN node:Document THEN node.description END AS doc_description, part.name AS part_name
</example>
<example>
question: Who are the suppliers for the part Turbo-Motor-11234?
cypher: MATCH (p:Part {{name: 'Turbo-Motor-11234'}})-[:supplied_by]-(s:Supplier) RETURN s.name AS supplier_name 
</example>

Note: Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything else than for you to construct a Cypher statement.
Do not include any text except the generated Cypher statement.

The question is:
{question}
\n"""

    CUSTOM_QA_TEMPLATE= """You are an assistant that helps to form nice and human understandable answers.
The information part contains the provided information that you must use to construct an answer.
The provided information is authoritative, you must never doubt it or try to use your internal knowledge to correct it.
Make the answer sound as a response to the question. 
Construct the text based on the information and result.
Information:
{context}

Question: {question}
Helpful Answer:"""

    EXAMPLE_QUERY = '''
##### Traceability
            
1. Tell me about the quality defect QC-1234-1?
2. List the part and documents associated with the defect QC-1234-1.
3. Give me the requirements for the part Turbo-Motor-11234.
4. What is the production order associated with the defect QC-1234-1?

##### Supplier Quality
1. Who are the suppliers for the part Turbo-Motor-11234?
2. Which supplier is recommended for part Turbo-Motor-11234 based on highest quality score?
3. What is the lead time and corrective action response time for Max Holdings?
4. Do you have a SOP? please provide me the SOP url.

##### Sustainability
1. Can you provide the lca, pcf and scope3 emissions data for the part Turbo-Motor-11234?
2. What is the supply chain transparency index for the part Turbo-Motor-11234?

##### Access
1. Who can access the project Turbo-Project?
2. Can Emily access the project Turbo-Project?
3. What is the status of the project Turbo-Project?
                    
##### Predictive Maintenance
1. When is the next scheduled maintenance for the part Turbo-Motor-11234?
2. Are there any anomalies detected for the part Turbo-Motor-11234?
3. Any historical trend suggestions for the part Turbo-Motor-11234?
                    
'''

    app_description = "Manufacturing organizations have vast amounts of knowledge dispersed across the product lifecycle, which can result in limited visibility, knowledge gaps, and the inability to continuously improve. A digital thread offers an integrated approach to combine disparate data sources across enterprise systems to drive traceability, accessibility, collaboration, and agility. In this demo, learn how to create an intelligent manufacturing digital thread using a combination of knowledge graph and generative AI technologies based on data generated throughout the product lifecycle, and their interconnected relationship. Explore use cases and discover actionable steps to start your intelligent digital thread journey."

    @staticmethod
    def get_cypher_custom_template():
        return AppConfig.CYPHER_CUSTOM_TEMPLATE

    @staticmethod
    def get_custom_qa_template():
        return AppConfig.CUSTOM_QA_TEMPLATE
    
    @staticmethod
    def get_neptune_host():
        return AppConfig.NEPTUNE_HOST

    @staticmethod
    def get_neptune_port():
        return AppConfig.NEPTUNE_PORT
    
    @staticmethod
    def get_app_description():
        return AppConfig.app_description
    
    @staticmethod
    def get_example_query():
        return AppConfig.EXAMPLE_QUERY
    
    @staticmethod
    def get_cognito_pool_id():
        return AppConfig.cognito_pool_id
    
    @staticmethod
    def get_cognito_app_client_id():
        return AppConfig.cognito_app_client_id
    
    @staticmethod
    def get_cognito_app_client_secret():
        return AppConfig.cognito_app_client_secret
    





