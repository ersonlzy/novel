from components.llm import LLM


class NovelGenerator(LLM):
    def __init__(self, model, model_provider, model_kwargs={}):
        from prompts.novel_generator import system_prompt, user_prompt, user_input, schemas
        super().__init__(model, model_provider, model_kwargs, system_prompt, user_prompt, user_input, schemas)
        self.get_chain()

    def invoke(self, inputs):
        target_num = int(inputs.get("words_num"))
        
        full_content = ""
        
        retry_count = 0
        max_retries = 3
        
        inputs.update({"generated_content": full_content})
        
        current_inputs = inputs.copy()
        
        while len(full_content) < target_num and retry_count < max_retries + 1:
            if "generated_content" in current_inputs:
                current_inputs["generated_content"] += full_content
            
            continuation_instruction = f"\n\n当前章节字数不足（已生成{len(full_content)}字，目标{target_num}字）。请继续扩写本章节，直到满足字数要求。"
            current_inputs["user_input"] = inputs["user_input"] + continuation_instruction
            new_res = super().invoke(current_inputs)
            full_content = str(new_res)
            retry_count += 1
            
        return full_content

class OutlinesGenerator(LLM):
    def __init__(self, model, model_provider, model_kwargs={}):  
        from prompts.outline_generator import system_prompt, user_prompt, user_input, schemas
        super().__init__(model, model_provider, model_kwargs, system_prompt, user_prompt, user_input, schemas)
        self.get_chain()    