from components.llm import LLM



class QueriesExtractor(LLM):
    def __init__(self, model, model_provider, model_kwargs={}):
        from prompts.queries_extractor import system_prompt, user_prompt, user_input, schemas
        super().__init__(model, model_provider, model_kwargs, system_prompt, user_prompt, user_input, schemas)
        self.get_chain()

    