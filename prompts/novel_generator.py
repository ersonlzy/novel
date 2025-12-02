from langchain_classic.output_parsers import ResponseSchema


system_prompt = "你是一位专业的小说写作家"



user_prompt = """
    ## 工作流描述
    你需要根据当前章节内容以及小说的各项设定、背景、人物设定等，对当前章节内容进行补充**扩写**。
    注意，你只需要专注**本章节内容**的扩写工作，不得涉及未来章节具体的情节描写。
    你需要利用各种背景知识丰富故事内容，可适当添加新的剧情，但需要保证上下文一致。
    所生成的小说要注意以下几点：
    1. **小说正文不小于{words_num}个字**，这是一个**硬性要求**，请务必遵守。如果内容不足，请继续扩展细节、对话和心理描写。
    2. **上下文内容细节一致**
    3. **满足用户的要求**
    4. **故事情节需要符合实际、逻辑严谨**
    5. 以第三人称进行创作，除非用户有特别指定
    6. 使用**中文**回复用户

    ## 生成风格要求
    1. 你只需要返回你所生成的小说内容，而不需要返回任何不相关的其他信息。
    2. 使用平易近人的语言，使用简单和通俗易懂的词汇，不要使用专业术语，使文章更加亲切和易于理解。
    3. 要使用短句，不要使用长句，不要冗长描述，便于阅读和理解。
    4. 使用口语化、接地气、人情味、富有情感的文字米描述。
    5. 段落过度要自然、逻辑清晰。不要使用“首先、其次、再次、然后、最后”这些副词和过渡词。
    6. 你所需要生成的内容为网络小说，你可以适当使用大尺度的细节描写以增强文学艺术性。

    ## 返回值
    你需要返回的值有：
    1. 章节标题
    2. 章节正文
    返回值格式要求：
    {return_format}
    """

user_input = """
    ## 用户要求
    {user_input}

    ## 未满足字数要求的生成内容
    {generated_content}

    ## 本章节大纲内容
    {local_outline}

    ## 前情提要
    {previous_content}

    ## 当前大纲临时设定
    {temp_settings}

    ## 背景知识
    {knowledge_context}

    ## 小说大纲知识
    {outline_settings}

    ## 装备知识
    {equipment_settings}

    ## 角色设定
    {character_settings}
"""

schemas = [
    ResponseSchema(name="title", type="string", description="章节标题."),
    ResponseSchema(name="content", type="string", description="章节正文"),
]