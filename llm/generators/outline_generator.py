"""
大纲生成器模块
合并了原 components/generators.py 中的 OutlinesGenerator 和 prompts/outline_generator.py
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一位专业的小说大纲架构师"

USER_PROMPT = """
    ## 工作流描述
    你需要根据用户输入的大纲描述，对当前大纲内容进行情节拆分，**生成{chapter_num}个章节的结构化大纲**。
    
    ## 任务目标
    1. 将宏大的故事拆解为{chapter_num}个具体的章节单位。
    2. **不要写正文！不要写正文！** 只需要提供每章的剧情梗概和关键节点。
    
    ## 章节大纲要求
    1. **每章字数**：控制在100-300字之间，言简意赅。
    2. **内容结构**：
       - **主要事件**：本章发生了什么核心冲突或转折。
       - **关键信息**：出场人物、重要地点、获得的线索/物品。
       - **伏笔/悬念**：本章结尾留下的悬念或为后续埋下的伏笔。
    3. **逻辑连贯**：章节之间必须有因果关系，时间线清晰。
    4. **满足要求**：严格贴合用户的创作方向。
    5. **严禁**：不要进行大段的环境描写、心理描写或对话描写。那是正文阶段做的事。
    6. **格式**：不要在内容中包含"第X章"这样的标题，只需返回大纲内容。

    ## 示例（One-Shot）
    **输入**：生成2章关于侦探寻找失猫的大纲。
    **输出**：
    [
        "某侦探在事务所接到一位老妇人的委托，寻找她失踪的波斯猫。侦探走访了老妇人所在的社区，发现最近有多起宠物失踪案。他在公园角落发现了一些奇怪的猫粮残渣，并遇到了一位行踪可疑的流浪汉。",
        "侦探跟踪流浪汉来到一处废弃工厂，发现这里竟然是一个非法宠物交易的中转站。侦探潜入工厂，试图寻找证据，却不小心触发了警报。在逃离过程中，他救下了老妇人的猫，并拍下了交易现场的照片作为证据。"
    ]

    ## 生成格式
    1. 返回一个字符串列表，列表中的每一项对应一个章节的大纲。
    2. 使用**中文**。

    ## 返回值
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
