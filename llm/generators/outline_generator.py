"""
大纲生成器模块
合并了原 components/generators.py 中的 OutlinesGenerator 和 prompts/outline_generator.py
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一位专业的小说写作家"

USER_PROMPT = """
    ## 工作流描述
    你需要根据用户输入的大纲描述，对当前大纲内容进行情节拆分，**生成{chapter_num}个章节大纲**。
    你需要利用各种背景知识丰富故事内容，可适当添加新的剧情，但需要保证上下文一致。
    
    所生成的章节大纲要注意以下几点：
    1. **每个章节大纲不应少于200字**，需包含足够的情节细节
    2. **上下文内容细节一致**，确保章节之间逻辑连贯
    3. **满足用户的要求**，紧扣用户提出的创作方向
    4. **故事情节需要符合实际、逻辑严谨**，避免出现逻辑漏洞
    5. 以第三人称进行创作，除非用户有特别指定
    6. 使用**中文**回复用户

    ## 生成风格要求
    1. 只返回所生成的章节大纲内容，不要返回任何解释或其他无关信息
    2. 使用平易近人的语言，使用简单通俗易懂的词汇，避免专业术语
    3. 使用短句，避免冗长复杂的句子，便于阅读和理解
    4. 使用口语化、接地气、富有人情味和情感的文字来描述
    5. 段落过渡要自然、逻辑清晰。避免使用"首先、其次、再次、然后、最后"等生硬的过渡词
    6. 你所需要生成的内容为网络小说大纲，可以适当包含细节描写以增强可读性

    ## 返回值
    1. 包含了正确数量的的章节大纲列表
    返回值格式要求：
    {return_format}
"""

USER_INPUT = """
    ## 用户要求
    {user_input}

    ## 当前大纲描述
    {outlines_description}

    ## 全局大纲设定
    {outline_settings}

    ## 角色设定
    {character_settings}

    ## 前文内容
    {previous_content}

    ## 背景知识
    {knowledge_context}

    ## 装备知识
    {equipment_settings}
"""

SCHEMAS = [
    ResponseSchema(name="outlines", type="list[string]", description="大纲列表"),
]


class OutlinesGenerator(LLM):
    """大纲生成器"""
    
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
