"""
小说生成工作流
重构自 workflows/novel_wf.py，更新导入路径并优化结构
"""
from llm.generators.novel_generator import NovelGenerator
from llm.generators.outline_generator import OutlinesGenerator
from llm.generators.detailed_outline_generator import DetailedOutlineGenerator
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
        if model and model_provider:
            self.novel_generator = NovelGenerator(model, model_provider, model_kwargs)
            self.outlines_generator = OutlinesGenerator(model, model_provider, model_kwargs)
            self.detailed_outline_generator = DetailedOutlineGenerator(model, model_provider, model_kwargs)
            
            # 如果没有配置特殊模型，使用主模型
            if special_model_provider and extractor_model and short_model:
                self.extractor = QueriesExtractor(extractor_model, special_model_provider, {"temperature": 0.5})
                self.shorter = ContentShorter(short_model, special_model_provider, {"temperature": 0.5})
            else:
                # 使用主模型作为特殊模型
                print(f"特殊模型未配置，使用主模型: {model_provider}/{model}")
                self.extractor = QueriesExtractor(model, model_provider, {"temperature": 0.5})
                self.shorter = ContentShorter(model, model_provider, {"temperature": 0.5})
        
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
        """生成章节大纲"""
        if progress_callback:
            progress_callback(0.1)
        
        print("开始检索相关信息...")
        query_results = self.retrieve_infos(inputs)
        if progress_callback:
            progress_callback(0.5)
        
        print("开始生成章节大纲...")
        inputs.update(query_results)
        outlines = self.outlines_generator.invoke(inputs)
        if progress_callback:
            progress_callback(0.9)
        
        # 格式化输出，添加章节编号
        outline_list = outlines["outlines"]
        formatted_outlines = [f"第{i}章：{outline}" for i, outline in enumerate(outline_list, 1)]
        outline_str = "\n\n".join(formatted_outlines)
        print(f"大纲生成完成，共{len(outline_list)}个章节")
        return outline_str, outline_list

    def generate_detailed_outlines(self, inputs: dict, progress_callback=None):
        """生成细纲"""
        if progress_callback:
            progress_callback(0.05)
        
        # 获取章节大纲列表
        chapter_outlines = inputs.get("chapter_outlines", [])
        if not chapter_outlines:
            raise ValueError("需要先生成章节大纲")
        
        print(f"开始为{len(chapter_outlines)}个章节生成细纲...")
        # 检索上下文信息
        query_results = self.retrieve_infos(inputs)
        inputs.update(query_results)
        
        if progress_callback:
            progress_callback(0.15)
        
        # 为每个章节生成细纲
        all_detailed_outlines = []
        total_chapters = len(chapter_outlines)
        progress_per_chapter = 70 / total_chapters
        
        for i, chapter_outline in enumerate(chapter_outlines, 1):
            print(f"正在生成第{i}/{total_chapters}章细纲...")
            
            chapter_inputs = {
                "chapter_outline": chapter_outline,
                "outline_settings": inputs.get("outline_settings", []),
                "character_settings": inputs.get("character_settings", []),
                "previous_content": inputs.get("previous_content", []),
                "knowledge_context": inputs.get("knowledge_context", []),
                "equipment_settings": inputs.get("equipment_settings", []),
                "temp_settings": inputs.get("temp_settings", "")
            }
            
            detailed_outline_result = self.detailed_outline_generator.invoke(chapter_inputs)
            detailed_outlines = detailed_outline_result["detailed_outlines"]
            all_detailed_outlines.append({
                "chapter_outline": chapter_outline,
                "detailed_outlines": detailed_outlines
            })
            
            if progress_callback:
                current_progress = (15 + i * progress_per_chapter) / 100
                progress_callback(current_progress)
        
        if progress_callback:
            progress_callback(0.9)
        
        # 格式化输出
        detailed_outline_str = ""
        for i, item in enumerate(all_detailed_outlines, 1):
            detailed_outline_str += f"### 章节 {i}\n"
            detailed_outline_str += f"**章节大纲：** {item['chapter_outline']}\n\n"
            detailed_outline_str += "**细纲：**\n"
            for j, detail in enumerate(item['detailed_outlines'], 1):
                detailed_outline_str += f"{j}. {detail}\n"
            detailed_outline_str += "\n"
        
        print("细纲生成完成")
        return detailed_outline_str, all_detailed_outlines

    def generate_novels(self, inputs, progress_callback=None, status_callback=None):
        """生成小说章节"""
        if progress_callback:
            progress_callback(10 / 100)
        
        local_outlines = inputs["generated_outlines"]
        total_chapters = len(local_outlines)
        print(f"开始生成{total_chapters}个章节的小说内容...")
        
        if status_callback:
            status_callback(f"📚 准备生成 {total_chapters} 个章节...")
        
        res_content = ""
        query_results = self.retrieve_infos(inputs)
        inputs.update(query_results)
        previous_content = inputs["previous_content"]
        
        if progress_callback:
            progress_callback(20 / 100)
        
        # 计算每个章节的进度步长（0-60%的进度）
        progress_per_chapter = 60 / total_chapters
        
        for i, local_outline in enumerate(local_outlines, 1):
            if not local_outline:
                continue
            
            print(f"\n正在生成第{i}/{total_chapters}章...")
            if status_callback:
                status_callback(f"✍️ 正在生成第 {i}/{total_chapters} 章...")
            
            base_progress = 20 + (i - 1) * progress_per_chapter
            
            if i > 1:
                # 缩写前文
                if status_callback:
                    status_callback(f"📝 第 {i}/{total_chapters} 章：正在整理前文...")
                
                if progress_callback:
                    progress_callback((base_progress + progress_per_chapter * 0.1) / 100)
                
                shorted_res = self.shorter.invoke({
                    "current_content": res_content, 
                    "next_outline": local_outline, 
                    "previous_content": previous_content
                })
                previous_content += f"\\n{shorted_res['shorted_content']}"
                next_outline = shorted_res["next_outline"]
            else:
                next_outline = local_outline
            
            if status_callback:
                status_callback(f"🎨 第 {i}/{total_chapters} 章：开始创作...")
            
            if progress_callback:
                progress_callback((base_progress + progress_per_chapter * 0.3) / 100)
            
            # 生成章节内容
            gen_inputs = {
                "local_outline": next_outline,
                "previous_content": previous_content,
            }
            inputs.update(gen_inputs)
            
            # 重试机制
            for retry in range(3):
                try:
                    res_content = self.novel_generator.invoke(inputs)
                    break
                except OutputParserException as e:
                    if retry == 2:
                        print(f"章节{i}生成失败: {e}")
                        if status_callback:
                            status_callback(f"❌ 第 {i}/{total_chapters} 章生成失败")
                        res_content = ""
                    else:
                        if status_callback:
                            status_callback(f"⚠️ 第 {i}/{total_chapters} 章：重试中... ({retry+1}/3)")
                    continue
            
            if progress_callback:
                progress_callback((base_progress + progress_per_chapter) / 100)
            
            if res_content and status_callback:
                status_callback(f"✅ 第 {i}/{total_chapters} 章完成 ({len(res_content)} 字)")
            
            yield res_content
