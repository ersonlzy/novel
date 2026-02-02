"""
细纲生成器模块
为章节大纲生成更详细的段落级别细纲
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一位专业的小说写作家，擅长将章节大纲拆分为详细的场景描写细纲"

USER_PROMPT = """
    ## 工作流描述
    你需要根据提供的章节大纲，将其拆分为更详细的**场景级别**细纲。
    每个场景细纲应该包含具体的场景地点、人物行为、对话焦点、心理活动等细节。
    你需要利用各种背景知识丰富故事内容，确保细节合理、逻辑严谨。
    
    所生成的细纲要注意以下几点：
    1. **每个场景细纲应在100-200字之间**
    2. **场景数量应在3-6个之间，视章节大纲复杂度而定**
    3. **细节描述要具体，包含人物动作、对话要点、场景氛围等**
    4. **上下文内容细节一致**
    5. **故事情节需要符合实际、逻辑严谨**
    6. 以第三人称进行创作，除非用户有特别指定
    7. 使用**中文**回复用户

    ## 生成风格要求
    1. 你只需要返回你所生成的场景细纲内容，而不需要返回任何不相关的其他信息。
    2. 使用平易近人的语言，使用简单和通俗易懂的词汇，不要使用专业术语，使文章更加亲切和易于理解。
    3. 要使用短句，不要使用长句，不要冗长描述，便于阅读和理解。
    4. 使用口语化、接地气、富有人情味和情感的文字来描述
    5. 场景过渡要自然、逻辑清晰。
    6. 你所需要生成的内容为网络小说场景细纲，你可以适当使用大尺度的细节描写以增强文学艺术性。

    ## 返回值
    1. 包含合适数量的段落细纲列表（3-8个）
    返回值格式要求：
    {return_format}
"""

USER_INPUT = """
    ## 当前章节大纲
    {chapter_outline}

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
    
    ## 临时设定
    {temp_settings}
"""

SCHEMAS = [
    ResponseSchema(name="detailed_outlines", type="list[string]", description="段落细纲列表"),
]


class DetailedOutlineGenerator(LLM):
    """细纲生成器"""
    
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
