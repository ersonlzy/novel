"""
查询提取器模块
合并了原 components/extractors.py 和 prompts/queries_extractor.py
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一个知识库检索词提取器"

USER_PROMPT = """
    ## 工作描述
    你需要根据大纲内容，提取出需要检索的查询信息，以便后续从知识库中获取相关内容支持小说创作。

    ## 可供检索的知识库
    1. **小说上下文知识库**：存储之前章节的内容信息
    2. **公共知识库**：存储小说背景、世界观设定等相关信息
    3. **小说项目设定知识库**：存储小说大纲、角色设定、装备设定等相关信息

    ## 需要提取的检索关键字类别
    1. **大纲信息检索词** (outline_queries)：用于从项目设定知识库中获取相关大纲信息
    2. **上下文检索词** (context_queries)：用于从上下文知识库中获取之前章节内容
    3. **背景知识检索词** (knowledge_queries)：用于从公共知识库中获取相关背景知识
    4. **角色设定检索词** (character_queries)：用于从项目设定知识库中获取相关角色设定
    5. **装备设定检索词** (equipment_queries)：用于从项目设定知识库中获取相关装备、道具设定

    ## 注意事项
    1. 每个检索词需要简洁、准确、具有代表性
    2. 只提供检索词列表，不需要其他解释或说明
    3. 根据不同的检索类别，生成对应的检索词列表
    4. **不能忽略任何检索类别**，必须提供所有5个类别的检索词列表
    5. 如果某个类别没有需要检索的内容，返回空列表 []


    ## Returns
    The format of the returns should be a json data, you can't ignore any key-item pair in the returns, if the corresponding item fo a key is empty, please set its item as empty string instead.
    返回值格式要求：
    {return_format}
"""

USER_INPUT = """
    ## 临时大纲设定
    {outlines_description}
    ## 临时设定
    {temp_settings}
    ## 用户要求
    {user_input}
"""

SCHEMAS = [
    ResponseSchema(name="outline_queries", type="list[string]", description="the list of queries of outline informations needed to be retrieved, default as []"),
    ResponseSchema(name="context_queries", type="list[string]", description="the list of queries of context informations needed to be retrieved, default as []"),
    ResponseSchema(name="knowledge_queries", type="list[string]", description="the list of queries of knowledge context informations needed to be retrieved, default as []"),
    ResponseSchema(name="character_queries", type="list[string]", description="the list of queries of character settings context informations needed to be retrieved, default as []"),
    ResponseSchema(name="equipment_queries", type="list[string]", description="the list of queries of arms, tools, weapon etc. context informations needed to be retrieved, default as []")
]


class QueriesExtractor(LLM):
    """查询提取器"""
    
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
