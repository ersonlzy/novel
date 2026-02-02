"""
查询重写器模块
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一个专业的搜索查询优化大师"

USER_PROMPT = """
    ## 任务描述
    你需要基于用户提供的原始查询词 (Query)，生成3个不同维度的改写查询词，以提高知识库检索的召回率。
    
    ## 改写策略
    1. **语义扩展**：使用同义词或近义词替换核心词汇
    2. **具体化**：将宽泛的概念具体化为可能的细节场景
    3. **关联发散**：联想与查询主题强相关的背景概念

    ## 输入查询
    {query}

    ## 要求
    1. 改写的查询词必须使用中文
    2. 保持与原意的高度相关性
    3. 只需要提供改写后的列表，不需要解释

    ## 返回值
    返回值格式要求：
    {return_format}
"""

USER_INPUT = """
    {query}
"""

SCHEMAS = [
    ResponseSchema(name="rewritten_queries", type="list[string]", description="改写后的查询词列表"),
]


class QueryRewriter(LLM):
    """查询重写器"""
    
    def __init__(self, model, model_provider, model_kwargs={}):
        super().__init__(
            model, 
            model_provider, 
            model_kwargs, 
            SYSTEM_PROMPT, 
            USER_PROMPT, 
            USER_INPUT, 
            SCHEMAS
        )
        self.get_chain()
