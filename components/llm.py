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
        except:
            return res  

    def __get_llm(self, model, model_provider:str, stream=False, model_kwargs={}):
        base_url = os.getenv(f"{model_provider.upper()}_BASE_URL", None)
        api_key = os.getenv(f"{model_provider.upper()}_API_KEY", None)
        if base_url is None and api_key is None:
            raise ValueError(f"Invalid model provider: {model_provider}, please check your model setting")
        if model_provider == "ollama":
            _get_llm = OllamaLLM
        else:
            model_provider = "openai"
            _get_llm = init_chat_model
        return _get_llm(
            model=model, 
            model_provider=model_provider, 
            base_url=base_url, 
            api_key=api_key, 
            disable_streaming=not stream, 
            **model_kwargs
        ) 

