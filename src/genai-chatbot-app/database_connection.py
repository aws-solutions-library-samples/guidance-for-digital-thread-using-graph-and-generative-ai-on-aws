
import logging
from langchain_aws.graphs import NeptuneGraph

class DatabaseConnection:
    def __init__(self, host, port, use_https):
        self.host = host
        self.port = port
        self.use_https = use_https

    def connect(self):
        logging.info('Connecting to DB', self.host, self.port, self.use_https)
        graph = NeptuneGraph(host=self.host, port=self.port, use_https=self.use_https)
        return graph