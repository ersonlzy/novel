"""
内容缩写器模块
合并了原 components/shorters.py 和 prompts/content_shorter.py
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一位专业的小说写作家"

USER_PROMPT = """
    ## 工作描述
    1. 你将会收到用户输入的当前章节内容、前几个章节内容（已被缩写）、下一章节大纲内容；
    2. 你需要缩写给到的当前章节内容，在缩小小说字数的同时，保证上下章节之间的信息一致性；
    3. 缩写后的章节内容应该保留人物、地点、事件等细节，并根据前文内容扩写或改写下一章节大纲，保证上下文一致；
    4. 缩写后的章节内容应小于800字。

    ## Returns Format
    你需要返回的内容有：
    1. 缩写后的小说内容
    2. 下一个章节的大纲
    返回值格式要求：
    {return_format}
"""

USER_INPUT = """
    ## 当前章节内容
    {current_content}

    ## 下一章节大纲
    {next_outline}

    ## 已生成章节内容
    {previous_content}
"""

SCHEMAS = [
    ResponseSchema(name="shorted_content", type="string", description="缩写后的章节内容"),
    ResponseSchema(name="next_outline", type="string", description="下一个章节大纲。"),
]


class ContentShorter(LLM):
    """内容缩写器"""
    
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
