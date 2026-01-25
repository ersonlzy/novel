"""
小说生成器模块
合并了原 components/generators.py 中的 NovelGenerator 和 prompts/novel_generator.py
"""
from langchain_classic.output_parsers import ResponseSchema
from llm.providers.base import LLM


# 提示词模板
SYSTEM_PROMPT = "你是一位专业的小说写作家"

USER_PROMPT = """
    ## 工作流描述
    你需要根据当前章节内容以及小说的各项设定、背景、人物设定等，对当前章节内容进行补充**扩写**。
    注意，你只需要专注**本章节内容**的扩写工作，不得涉及未来章节具体的情节描写。
    你需要利用各种背景知识丰富故事内容，可适当添加新的剧情，但需要保证上下文一致。
    
    所生成的小说要注意以下几点：
    1. **小说正文不小于{words_num}个字**，这是硬性要求，必须严格遵守。如果内容不足，请通过增加细节描写、对话、心理活动等方式扩充到目标字数。
    2. **上下文内容细节一致**，确保人物性格、场景描述、时间线等信息前后呼应
    3. **满足用户的要求**，紧扣用户提出的创作需求
    4. **故事情节需要符合实际、逻辑严谨**，避免出现逻辑漏洞
    5. 以第三人称进行创作，除非用户有特别指定
    6. 使用**中文**回复用户

    ## 生成风格要求
    1. 只返回所生成的小说内容，不要返回任何解释、说明或其他无关信息
    2. 使用平易近人的语言，使用简单通俗易懂的词汇，避免专业术语，使文章更加亲切和易于理解
    3. 使用短句，避免冗长复杂的句子，保持行文简洁流畅
    4. 使用口语化、接地气、富有人情味和情感的文字来描述
    5. 段落过渡要自然、逻辑清晰。避免使用"首先、其次、再次、然后、最后"等生硬的过渡词
    6. 你所需要生成的内容为网络小说，可以适当使用细节描写以增强文学艺术性和沉浸感

    ## 返回值
    你需要返回的值有：
    1. 章节标题
    2. 章节正文
    返回值格式要求：
    {return_format}
    """

USER_INPUT = """
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

SCHEMAS = [
    ResponseSchema(name="title", type="string", description="章节标题."),
    ResponseSchema(name="content", type="string", description="章节正文"),
]


class NovelGenerator(LLM):
    """小说生成器"""
    
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

    def invoke(self, inputs):
        """生成小说内容，采用累积式生成确保达到目标字数"""
        target_num = int(inputs.get("words_num"))
        full_content = ""
        retry_count = 0
        max_retries = 5  # 增加重试次数以支持累积生成
        
        print(f"目标字数: {target_num}字")
        
        # 累积式生成：首次生成初稿，后续续写累积
        while len(full_content) < target_num and retry_count < max_retries:
            current_inputs = inputs.copy()
            
            if retry_count == 0:
                # 第一次：生成初稿
                print("正在生成初稿...")
                current_inputs["generated_content"] = ""
                
            else:
                # 后续：在已有内容基础上续写
                shortage = target_num - len(full_content)
                print(f"\n第{retry_count + 1}次续写 (已有{len(full_content)}字，还需{shortage}字)...")
                
                # 构建续写提示
                continuation_hint = f"""
【续写任务】
当前章节已生成{len(full_content)}字内容，距离目标{target_num}字还差{shortage}字。

**请在以下已生成内容的基础上继续创作**：
- 保持叙事风格、人物性格、场景氛围的一致性
- 自然延续情节发展，不要突兀或重复
- 继续扩充细节、对话、心理活动等，确保内容充实
- 目标新增{min(shortage, 1500)}字左右

已生成内容：
{full_content[-500:] if len(full_content) > 500 else full_content}
...

请从上述内容自然延续，继续创作：
"""
                current_inputs["user_input"] = inputs.get("user_input", "") + "\n\n" + continuation_hint
                current_inputs["generated_content"] = full_content
            
            # 调用LLM生成
            try:
                new_res = super().invoke(current_inputs)
                new_content = str(new_res)
                
                if retry_count == 0:
                    # 初稿：直接使用
                    full_content = new_content
                    print(f"✓ 初稿生成完成: {len(full_content)}字")
                else:
                    # 续写：累积追加
                    # 清理可能的重复开头
                    if len(full_content) > 100 and new_content[:50] in full_content[-200:]:
                        # 检测到重复，尝试从重复点后开始
                        overlap_idx = full_content.rfind(new_content[:50])
                        if overlap_idx > 0:
                            new_content = new_content[50:]
                    
                    full_content += "\n\n" + new_content
                    print(f"✓ 续写完成: 新增{len(new_content)}字，累计{len(full_content)}字")
                
                retry_count += 1
                
                # 如果已经达到或接近目标（95%以上），提前结束
                if len(full_content) >= target_num * 0.95:
                    print(f"✓ 已达到字数要求！最终字数: {len(full_content)}字")
                    break
                    
            except Exception as e:
                print(f"✗ 生成出错: {e}")
                retry_count += 1
                if retry_count >= max_retries:
                    break
                continue
        
        # 最终检查
        if len(full_content) < target_num:
            completion_rate = (len(full_content) / target_num) * 100
            print(f"⚠ 字数未完全达标: {len(full_content)}/{target_num}字 ({completion_rate:.1f}%)，已返回所有生成内容")
        else:
            print(f"✅ 生成成功！最终字数: {len(full_content)}字")
            
        return full_content

