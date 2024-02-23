from langchain.chains import NeptuneOpenCypherQAChain

class QAChain:
    def __init__(self, llm, graph, qa_prompt, cypher_prompt):
        self.llm = llm
        self.graph = graph
        self.qa_prompt = qa_prompt
        self.cypher_prompt = cypher_prompt

    def create(self):
        chain = NeptuneOpenCypherQAChain.from_llm(llm=self.llm, 
                                                  graph=self.graph, 
                                                  qa_prompt=self.qa_prompt,
                                                  cypher_prompt=self.cypher_prompt,
                                                  verbose=False, 
                                                  top_K=10, 
                                                  return_intermediate_steps=True,
                                                  return_direct=False)
        return chain