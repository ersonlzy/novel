from components.generators import NovelGenerator, OutlinesGenerator
from components.extractors import QueriesExtractor
from components.shorters import ContentShorter
from rag.retrievers import Retriever
from utils.tools import get_config
from threading import Thread


class Novel():
    def __init__(self, config_path, model=None, model_provoder=None, extractor_model=None, short_model=None, special_model_provider=None, model_kwargs={}):
        self.args = get_config(config_path)
        if model and model_provoder and extractor_model and short_model and special_model_provider:
            self.novel_generator = NovelGenerator(model, model_provoder, model_kwargs)
            self.outlines_generator = OutlinesGenerator(model, model_provoder, model_kwargs)
            self.extractor = QueriesExtractor(extractor_model, special_model_provider, {"temperature": 0.5})
            self.shorter = ContentShorter(short_model, special_model_provider, {"temperature": 0.5})
        self.project_retriever = Retriever(self.args.project_documents)
        self.knowledge_retriever = Retriever(self.args.knowledge_documents)
        self.context_retriever = Retriever(self.args.context_documents)



    
    def update(self):
        self.project_retriever.update()
        self.knowledge_retriever.update()
        self.context_retriever.update()

    def retrieve_infos(self, inputs):
        queries = self.extractor.invoke(inputs)
        print("检索关键词提取完成")
        query_results = self.query_context(queries)
        print("检索完成")
        return query_results

    def query_single(self, retriever:Retriever, queries:list, results:dict, key:str):
        result = retriever.invoke(queries)
        results.update({key: result})

    def query_context(self, inputs):
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
        return results

    def generate_outlines(self, inputs:dict, bar):
        bar.progress(10)
        query_results = self.retrieve_infos(inputs)
        bar.progress(50)
        inputs.update(query_results)
        outlines = self.outlines_generator.invoke(inputs)
        bar.progress(90)
        outline_str = "\n\n".join(outlines["outlines"])
        outline_list = outlines["outlines"]
        return outline_str, outline_list

    def generate_novels(self, inputs, bar):
        bar.progress(10 / 100)
        local_outlines = inputs["generated_outlines"]
        res_content = ""
        query_results = self.retrieve_infos(inputs)
        inputs.update(query_results)
        previous_content = inputs["previous_content"]
        bar.progress(20 / 100)
        # try:
        progress = 60 / len(local_outlines) / 5
        for i, local_outline in enumerate(local_outlines):
            bar.progress((progress * i * 5 + 21)/100)
            if local_outline:
                if i > 0:
                    shorted_res = self.shorter.invoke({"current_content": res_content, "next_outline": local_outline, "previous_content": previous_content})
                    previous_content += f"\n{shorted_res["shorted_content"]}"
                    next_outline = shorted_res["next_outline"]
                else:
                    next_outline = local_outline
                bar.progress((progress * i * 5 + 23)/100)
                gen_inputs = {
                    "local_outline": next_outline,
                    "previous_content": previous_content,
                }
                inputs.update(gen_inputs)
                res_content = self.novel_generator.invoke(inputs)
                bar.progress((progress * i * 5 + 25)/100)
                yield res_content
        # except Exception as e:
        #     print(f"Generate novel failed: {e}")
        #     yield False