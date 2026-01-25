from rag.processors import DocumentProcessor
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
import os




class Retriever():
    def __init__(self, documents, k=1):
        self.document_processor = DocumentProcessor(documents)
        self.base_retriever = self.document_processor.get_Chroma().as_retriever(search_type="mmr",kwargs={"k": 5})
        self.reranker = CohereRerank(cohere_api_key=os.getenv("SILICONFLOW_API_KEY"), base_url=os.getenv("SILICONFLOW_BASE_URL"), model="BAAI/bge-reranker-v2-m3")
        self.chain = ContextualCompressionRetriever(base_compressor=self.reranker, base_retriever=self.base_retriever)
        self.k = k
    
    def invoke(self, queries):
        """执行检索查询，返回合并后的结果"""
        if not queries:
            return ""
        
        query_results = []
        for query in queries:
            results = self.chain.invoke(query)[:self.k]
            for result in results:
                if result.page_content.strip():
                    query_results.append(result.page_content)
        
        return "\n\n".join(query_results) if query_results else ""

    def update(self):
        self.document_processor.update()