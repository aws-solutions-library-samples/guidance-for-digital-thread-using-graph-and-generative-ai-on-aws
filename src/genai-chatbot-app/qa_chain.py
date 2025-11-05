from langchain_aws.chains import create_neptune_opencypher_qa_chain

class QAChain:
    def __init__(self, llm, graph, qa_prompt, cypher_prompt):
        self.llm = llm
        self.graph = graph
        self.qa_prompt = qa_prompt
        self.cypher_prompt = cypher_prompt

    def create(self):
        chain = create_neptune_opencypher_qa_chain(llm=self.llm, 
                                                  graph=self.graph, 
                                                  qa_prompt=self.qa_prompt,
                                                  cypher_prompt=self.cypher_prompt,
                                                  return_intermediate_steps=True,
                                                  return_direct=False,
                                                  allow_dangerous_requests=True
                                                  )
        return chain