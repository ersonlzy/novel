"""
小说生成工作流
重构自 workflows/novel_wf.py，更新导入路径并优化结构
"""
from llm.generators.novel_generator import NovelGenerator
from llm.generators.outline_generator import OutlinesGenerator
from llm.generators.queries_extractor import QueriesExtractor
from llm.generators.content_shorter import ContentShorter
from rag.retrievers import Retriever
from config.project_config import get_config
from threading import Thread
from langchain_core.exceptions import OutputParserException


class NovelWorkflow:
    """小说生成工作流"""
    
    def __init__(self, config_path, model=None, model_provider=None, extractor_model=None, 
                 short_model=None, special_model_provider=None, model_kwargs={}):
        self.args = get_config(config_path)
        if model and model_provider and extractor_model and short_model and special_model_provider:
            self.novel_generator = NovelGenerator(model, model_provider, model_kwargs)
            self.outlines_generator = OutlinesGenerator(model, model_provider, model_kwargs)
            self.extractor = QueriesExtractor(extractor_model, special_model_provider, {"temperature": 0.5})
            self.shorter = ContentShorter(short_model, special_model_provider, {"temperature": 0.5})
        self.project_retriever = Retriever(self.args.project_documents)
        self.knowledge_retriever = Retriever(self.args.knowledge_documents)
        self.context_retriever = Retriever(self.args.context_documents)

    def update(self):
        """更新所有检索器"""
        self.project_retriever.update()
        self.knowledge_retriever.update()
        self.context_retriever.update()

    def retrieve_infos(self, inputs):
        """检索相关信息"""
        queries = self.extractor.invoke(inputs)
        print("检索关键词提取完成")
        query_results = self.query_context(queries)
        print("检索完成")
        return query_results

    def query_single(self, retriever: Retriever, queries: list, results: dict, key: str):
        """单个检索任务"""
        try:
            result = retriever.invoke(queries)
            results.update({key: result})
        except Exception as e:
            print(f"[ERROR] 检索任务 {key} 失败: {e}")
            results.update({key: []})

    def query_context(self, inputs):
        """并行检索上下文信息"""
        results = {}
        outline_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs["outline_queries"], results, "outline_settings"])
        character_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs["character_queries"], results, "character_settings"])
        knowledge_thread = Thread(target=self.query_single, args=[self.knowledge_retriever, inputs["knowledge_queries"], results, "knowledge_context"])
        previous_thread = Thread(target=self.query_single, args=[self.context_retriever, inputs["context_queries"], results, "previous_content"])
        equipment_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs["equipment_queries"], results, "equipment_settings"])
        threads = [outline_thread, character_thread, knowledge_thread, previous_thread, equipment_thread]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        if "outline_settings" not in results:
            results.update({"outline_settings": []})
        if "character_settings" not in results:
            results.update({"character_settings": []})
        if "knowledge_context" not in results:
            results.update({"knowledge_context": []})
        if "previous_content" not in results:
            results.update({"previous_content": []})
        if "equipment_settings" not in results:
            results.update({"equipment_settings": []})
        return results

    def generate_outlines(self, inputs: dict, progress_callback=None):
        """生成大纲"""
        if progress_callback:
            progress_callback(10)
        query_results = self.retrieve_infos(inputs)
        if progress_callback:
            progress_callback(50)
        inputs.update(query_results)
        outlines = self.outlines_generator.invoke(inputs)
        if progress_callback:
            progress_callback(90)
        outline_str = "\\n\\n".join(outlines["outlines"])
        outline_list = outlines["outlines"]
        return outline_str, outline_list

    def generate_novels(self, inputs, progress_callback=None):
        """生成小说章节"""
        if progress_callback:
            progress_callback(10 / 100)
        local_outlines = inputs["generated_outlines"]
        res_content = ""
        query_results = self.retrieve_infos(inputs)
        inputs.update(query_results)
        previous_content = inputs["previous_content"]
        if progress_callback:
            progress_callback(20 / 100)
        
        progress = 60 / len(local_outlines) / 5
        for i, local_outline in enumerate(local_outlines):
            if progress_callback:
                progress_callback((progress * i * 5 + 21) / 100)
            if local_outline:
                if i > 0:
                    shorted_res = self.shorter.invoke({
                        "current_content": res_content, 
                        "next_outline": local_outline, 
                        "previous_content": previous_content
                    })
                    previous_content += f"\\n{shorted_res['shorted_content']}"
                    next_outline = shorted_res["next_outline"]
                else:
                    next_outline = local_outline
                if progress_callback:
                    progress_callback((progress * i * 5 + 23) / 100)
                gen_inputs = {
                    "local_outline": next_outline,
                    "previous_content": previous_content,
                }
                inputs.update(gen_inputs)
                for _ in range(3):
                    try:
                        res_content = self.novel_generator.invoke(inputs)
                        break
                    except OutputParserException as e:
                        continue
                if progress_callback:
                    progress_callback((progress * i * 5 + 25) / 100)
                yield res_content
