from langchain_classic.output_parsers import ResponseSchema


system_prompt = "你是一个知识库检索词提取器"



user_prompt = """
    ## 工作描述：
    你需要根据大纲内容，提取出需要检索的查询信息，以便后续从知识库中获取相关内容支持小说创作。
    
 

    ## 目前可供检索的知识库有：
    1. 小说上下文知识库，储存了之前章节的内容信息。
    2. 公共知识库，储存了小说背景、设定等相关信息。
    3. 小说项目设定知识库，储存了小说大纲、角色设定、装备设定等相关信息。

    ## 你需要提取供检索使用的关键字有:
    1. 用于从项目设定知识库中获取相关大纲信息，返回的key名称为outline_queries;
    2. 用于从上下文知识库中获取之前章节内容，返回的key名称为context_queries;
    3. 用于从公共知识库中获取相关背景知识，返回的key名称为knowledge_queriest;
    4. 用于从项目设定知识库中获取相关角色设定内容，返回的key名称为character_queries;
    5. 用于从项目设定知识库中获取相关装备设定内容，返回的key名称为equipment_queries;


    ## 注意事项：
    1. 每个检索词需要简洁、准确。
    2. 你只需要提供检索词，不需要其他信息输出
    3. 你需要根据不同的检索类别，生成对应的检索词列表。
    4. 你不能忽略任何检索类别，必须提供所有检索词列表，如果某个类别没有需要检索的内容，可以返回空列表。


    ## Returns
    The format of the returns should be a json data, you can't ignore any key-item pair in the returns, if the corresponding item fo a key is empty, please set its item as empty string instead.
    返回值格式要求：
    {return_format}
"""

user_input = """
    ## 临时大纲设定
    {outlines_description}
    ## 临时设定
    {temp_settings}
    ## 用户要求
    {user_input}
"""

schemas = [
    ResponseSchema(name="outline_queries", type="list[string]", description="the list of queries of outline informations needed to be retrieved, default as []"),
    ResponseSchema(name="context_queries", type="list[string]", description="the list of queries of context informations needed to be retrieved, default as []"),
    ResponseSchema(name="knowledge_queries", type="list[string]", description="the list of queries of knowledge context informations needed to be retrieved, default as []"),
    ResponseSchema(name="character_queries", type="list[string]", description="the list of queries of character settings context informations needed to be retrieved, default as []"),
    ResponseSchema(name="equipment_queries", type="list[string]", description="the list of queries of arms, tools, weapon etc. context informations needed to be retrieved, default as []")
]