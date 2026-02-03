from rag.processors import DocumentProcessor
from langchain_classic.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain_cohere import CohereRerank
import os




class Retriever():
    def __init__(self, documents, k=1, query_rewriter=None):
        self.document_processor = DocumentProcessor(documents)
        self.base_retriever = self.document_processor.get_Chroma().as_retriever(search_type="mmr",kwargs={"k": 5})
        base_url = os.getenv("SILICONFLOW_BASE_URL")
        self.reranker = CohereRerank(
            cohere_api_key=os.getenv("SILICONFLOW_API_KEY"), 
            base_url=base_url, 
            model=os.getenv("DEFAULT_RERANKER_MODEL", "BAAI/bge-reranker-v2-m3")
        )
        self.chain = ContextualCompressionRetriever(base_compressor=self.reranker, base_retriever=self.base_retriever) # type: ignore
        self.k = k
        self.query_rewriter = query_rewriter
    
    def invoke(self, queries):
        """执行检索查询，返回合并后的结果"""
        if not queries:
            return ""
        
        # 如果配置了重写器，对查询进行扩充
        expanded_queries = set(queries) # 使用set去重
        if self.query_rewriter:
            for query in queries:
                try:
                    rewritten_res = self.query_rewriter.invoke({"query": query})
                    if rewritten_res and "rewritten_queries" in rewritten_res:
                         for q in rewritten_res["rewritten_queries"]:
                             expanded_queries.add(q)
                except Exception as e:
                    print(f"[Warn] Query rewriting failed for '{query}': {e}")
        
        final_queries = list(expanded_queries)
        print(f"检索优化：原始查询{len(queries)}个 -> 扩充后{len(final_queries)}个")
        
        query_results = []
        seen_content = set() # 用于内容去重
        
        for query in final_queries:
            results = self.chain.invoke(query)[:self.k]
            for result in results:
                content = result.page_content.strip()
                if content and content not in seen_content:
                    query_results.append(content)
                    seen_content.add(content)
        
        return "\n\n".join(query_results) if query_results else ""

    def update(self):
        self.document_processor.update()