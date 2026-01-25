from langchain_core.exceptions import OutputParserException
from langchain_classic.chat_models import init_chat_model
from langchain_classic.output_parsers import StructuredOutputParser, OutputFixingParser
from langchain_classic.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import os

class LLM():
    def __init__(self, model, model_provider, model_kwargs={}, system_prompt="", user_prompt="", user_input="{user_input}", schemas=None, stream=False):
        self.llm = self.__get_llm(model, model_provider, stream, model_kwargs)
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.user_input = user_input
        self.template = ChatPromptTemplate([
            ("system", self.system_prompt),
            ("system", self.user_prompt),
            ("user", self.user_input)
        ])
        if schemas:
            self.parser = StructuredOutputParser.from_response_schemas(schemas)
            self.fixing_parser = OutputFixingParser.from_llm(self.llm, self.parser, max_retries=3)
        else:
            self.parser = None # type: ignore
            self.fixing_parser = None # type: ignore

    def get_chain(self):
        if self.parser:
            self.chain = self.template | self.llm | self.fixing_parser
        else:
            self.chain = self.template | self.llm
            

    def invoke(self, inputs):
        if self.parser:
            inputs.update({"return_format": self.parser.get_format_instructions()})
        try_num = 0
        while True:
            try:
                res = self.chain.invoke(inputs)
            except OutputParserException as e:
                if try_num > 3:
                    raise e
                try_num += 1
                continue
            except Exception as e:
                raise e
            break
        try:
            return res["content"]
        except (KeyError, TypeError):
            return res  

    def __get_llm(self, model, model_provider:str, stream=False, model_kwargs={}):
        """初始化LLM客户端"""
        # 获取对应提供商的配置
        provider_upper = model_provider.upper()
        base_url = os.getenv(f"{provider_upper}_BASE_URL", None)
        api_key = os.getenv(f"{provider_upper}_API_KEY", None)
        
        # 调试信息
        print(f"\n==== LLM 初始化 ====")
        print(f"提供商: {model_provider}")
        print(f"模型: {model}")
        print(f"Base URL: {base_url}")
        print(f"API Key: {'已配置' if api_key and api_key != 'sk-' else '未配置或无效'}")
        print(f"==================\n")
        
        # 验证配置
        if base_url is None and api_key is None:
            raise ValueError(f"Invalid model provider: {model_provider}, please check your model setting")
        
        # 根据提供商选择LLM类型
        if model_provider.lower() == "ollama":
            _get_llm = OllamaLLM
            return _get_llm(
                model=model, 
                base_url=base_url, 
                **model_kwargs
            )
        else:
            # 其他提供商使用OpenAI兼容接口
            _get_llm = init_chat_model
            return _get_llm(
                model=model, 
                model_provider="openai",  # 使用OpenAI兼容接口
                base_url=base_url, 
                api_key=api_key, 
                disable_streaming=not stream, 
                **model_kwargs
            ) 

