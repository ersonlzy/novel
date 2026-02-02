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
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from langchain_core.exceptions import OutputParserException
import copy


from llm.generators.query_rewriter import QueryRewriter

class NovelWorkflow:
    """小说生成工作流"""
    
    def __init__(self, config_path, model=None, model_provider=None, extractor_model=None, 
                 short_model=None, special_model_provider=None, model_kwargs={}):
        self.args = get_config(config_path)
        self.query_rewriter = None
        
        if model and model_provider:
            self.novel_generator = NovelGenerator(model, model_provider, model_kwargs)
            self.outlines_generator = OutlinesGenerator(model, model_provider, model_kwargs)
            self.detailed_outline_generator = DetailedOutlineGenerator(model, model_provider, model_kwargs)
            self.query_rewriter = QueryRewriter(model, model_provider, {"temperature": 0.7}) # 使用较高的temperature增加多样性
            
            # 如果没有配置特殊模型，使用主模型
            if special_model_provider and extractor_model and short_model:
                self.extractor = QueriesExtractor(extractor_model, special_model_provider, {"temperature": 0.5})
                self.shorter = ContentShorter(short_model, special_model_provider, {"temperature": 0.5})
            else:
                # 使用主模型作为特殊模型
                print(f"特殊模型未配置，使用主模型: {model_provider}/{model}")
                self.extractor = QueriesExtractor(model, model_provider, {"temperature": 0.5})
                self.shorter = ContentShorter(model, model_provider, {"temperature": 0.5})
        
        # 将rewriter传入retriever
        self.project_retriever = Retriever(self.args.project_documents, query_rewriter=self.query_rewriter)
        self.knowledge_retriever = Retriever(self.args.knowledge_documents, query_rewriter=self.query_rewriter)
        self.context_retriever = Retriever(self.args.context_documents, query_rewriter=self.query_rewriter)

    def update(self):
        """更新所有检索器"""
        self.project_retriever.update()
        self.knowledge_retriever.update()
        self.context_retriever.update()

    def retrieve_infos(self, inputs):
        """检索相关信息"""
        print("开始提取检索关键词...")
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
        outline_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs.get("outline_queries", []), results, "outline_settings"])
        character_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs.get("character_queries", []), results, "character_settings"])
        knowledge_thread = Thread(target=self.query_single, args=[self.knowledge_retriever, inputs.get("knowledge_queries", []), results, "knowledge_context"])
        previous_thread = Thread(target=self.query_single, args=[self.context_retriever, inputs.get("context_queries", []), results, "previous_content"])
        equipment_thread = Thread(target=self.query_single, args=[self.project_retriever, inputs.get("equipment_queries", []), results, "equipment_settings"])
        threads = [outline_thread, character_thread, knowledge_thread, previous_thread, equipment_thread]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        # 确保所有key都存在
        for key in ["outline_settings", "character_settings", "knowledge_context", "previous_content", "equipment_settings"]:
            if key not in results:
                results[key] = ""
                
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
        formatted_outlines = []
        for i, outline in enumerate(outline_list, 1):
            # 清理可能存在的章节标题前缀
            clean_outline = outline.replace(f"第{i}章", "").replace(f"第{i}章：", "").replace("：", "", 1).strip()
            # 如果清理后开头还有冒号，再清理一次
            if clean_outline.startswith("：") or clean_outline.startswith(":"):
                 clean_outline = clean_outline[1:].strip()
            
            formatted_outlines.append(f"第{i}章：{clean_outline}")
            
        outline_str = "\n\n".join(formatted_outlines)
        print(f"大纲生成完成，共{len(outline_list)}个章节")
        return outline_str, outline_list

    def _generate_single_detailed_outline(self, chapter_inputs, index, total_chapters):
        """生成单个详细大纲的任务函数"""
        try:
            print(f"正在生成第{index}/{total_chapters}章细纲...")
            detailed_outline_result = self.detailed_outline_generator.invoke(chapter_inputs)
            detailed_outlines = detailed_outline_result["detailed_outlines"]
            return index, {
                "chapter_outline": chapter_inputs["chapter_outline"],
                "detailed_outlines": detailed_outlines
            }
        except Exception as e:
            print(f"生成第{index}章细纲失败: {e}")
            return index, None

    def generate_detailed_outlines(self, inputs: dict, progress_callback=None):
        """生成细纲 (并行优化版)"""
        if progress_callback:
            progress_callback(0.05)
        
        # 获取章节大纲列表
        chapter_outlines = inputs.get("chapter_outlines", [])
        if not chapter_outlines:
            raise ValueError("需要先生成章节大纲")
        
        print(f"开始为{len(chapter_outlines)}个章节生成细纲...")
        if len(chapter_outlines) < 2:
            print("[WARNING] 检测到的章节大纲数量少于2，可能生成了单一大块内容而不是分章大纲。")
        
        # 检索上下文信息
        query_results = self.retrieve_infos(inputs)
        inputs.update(query_results)
        
        if progress_callback:
            progress_callback(0.15)
        
        total_chapters = len(chapter_outlines)
        progress_per_chapter = 70 / total_chapters
        completed_count = 0
        progress_lock = Lock()
        
        # 准备结果列表，先用None填充
        all_detailed_outlines = [None] * total_chapters
        
        # 使用线程池并行生成
        # 限制最大并发数为 5，避免触发 API 限制
        max_workers = 5
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {}
            for i, chapter_outline in enumerate(chapter_outlines, 1):
                chapter_inputs = {
                    "chapter_outline": chapter_outline,
                    "outline_settings": inputs.get("outline_settings", ""),
                    "character_settings": inputs.get("character_settings", ""),
                    "previous_content": inputs.get("previous_content", ""),
                    "knowledge_context": inputs.get("knowledge_context", ""),
                    "equipment_settings": inputs.get("equipment_settings", ""),
                    "temp_settings": inputs.get("temp_settings", "")
                }
                future = executor.submit(self._generate_single_detailed_outline, chapter_inputs, i, total_chapters)
                future_to_index[future] = i

            for future in as_completed(future_to_index):
                index, result = future.result()
                if result:
                    all_detailed_outlines[index-1] = result
                
                with progress_lock:
                    completed_count += 1
                    if progress_callback:
                        current_progress = (15 + completed_count * progress_per_chapter) / 100
                        progress_callback(current_progress)

        if progress_callback:
            progress_callback(0.9)
        
        # 格式化输出
        detailed_outline_str = ""
        valid_outlines = [item for item in all_detailed_outlines if item is not None]
        
        for i, item in enumerate(valid_outlines, 1):
            detailed_outline_str += f"### 章节 {i}\n"
            detailed_outline_str += f"**章节大纲：** {item['chapter_outline']}\n\n"
            detailed_outline_str += "**细纲：**\n"
            for j, detail in enumerate(item['detailed_outlines'], 1):
                detailed_outline_str += f"{j}. {detail}\n"
            detailed_outline_str += "\n"
        
        print("细纲生成完成")
        return detailed_outline_str, valid_outlines

    def generate_novels(self, inputs, progress_callback=None, status_callback=None):
        """生成小说章节 (针对每个章节动态检索)"""
        if progress_callback:
            progress_callback(10 / 100)
        
        local_outlines = inputs["generated_outlines"]
        total_chapters = len(local_outlines)
        print(f"开始生成{total_chapters}个章节的小说内容...")
        
        if status_callback:
            status_callback(f"📚 准备生成 {total_chapters} 个章节...")
        
        # 初始全局检索（可选，保留一些全局上下文）
        global_context_inputs = inputs.copy()
        # 将大纲描述作为全局检索的一个依据
        global_query_results = self.retrieve_infos(global_context_inputs)
        
        # 初始化前文内容
        previous_content = global_query_results.get("previous_content", "")
        if "previous_content" in inputs and inputs["previous_content"]:
             previous_content = inputs["previous_content"] # 如果输入中已有前文，优先使用

        
        if progress_callback:
            progress_callback(20 / 100)
        
        progress_per_chapter = 80 / total_chapters # 剩余80%的进度分配给章节生成
        
        res_content = ""
        
        for i, local_outline in enumerate(local_outlines, 1):
            if not local_outline:
                continue
            
            print(f"\n正在处理第{i}/{total_chapters}章...")
            
            # 1. 动态检索上下文
            # 使用当前章节大纲和临时设定作为检索依据
            if status_callback:
                status_callback(f"🔍 第 {i}/{total_chapters} 章：正在检索相关信息...")
                
            chapter_retrieval_inputs = {
                "outlines_description": local_outline, # 使用本章大纲检索
                "temp_settings": inputs.get("temp_settings", ""),
                "user_input": inputs.get("user_input", "")
            }
            
            # 获取本章特定的上下文信息
            print(f"第{i}章：执行动态检索...")
            chapter_query_results = self.retrieve_infos(chapter_retrieval_inputs)
            
            # 合并全局上下文和本章特定上下文
            # 策略：优先使用本章特定的，如果为空则回退到全局的(或者合并)
            # 这里简单做合并或者覆盖，视具体需求。这里采用 "优先本章检索结果"
            current_chapter_context = global_query_results.copy()
            current_chapter_context.update(chapter_query_results)
            # 始终保持最新的 previous_content
            current_chapter_context["previous_content"] = previous_content

            
            # 2. 缩写/整理前文 (如果不是第一章)
            base_progress = 20 + (i - 1) * progress_per_chapter
            next_outline = local_outline

            if i > 1:
                if status_callback:
                    status_callback(f"📝 第 {i}/{total_chapters} 章：正在整理剧情连贯性...")
                
                # Update progress
                if progress_callback:
                    progress_callback((base_progress + progress_per_chapter * 0.1) / 100)
                
                try:
                    shorted_res = self.shorter.invoke({
                        "current_content": res_content, 
                        "next_outline": local_outline, 
                        "previous_content": previous_content
                    })
                    # 更新前文内容: 累加新的缩写内容
                    previous_content += f"\\n{shorted_res['shorted_content']}"
                    # 更新当前上下文中的前文
                    current_chapter_context["previous_content"] = previous_content
                    # 可能会优化大纲
                    next_outline = shorted_res.get("next_outline", local_outline)
                except Exception as e:
                    print(f"缩写前文失败: {e}，跳过缩写步骤")

            
            # 3. 生成内容
            if status_callback:
                status_callback(f"🎨 第 {i}/{total_chapters} 章：正在创作正文...")
            
            if progress_callback:
                progress_callback((base_progress + progress_per_chapter * 0.3) / 100)
            
            # 准备生成所需的完整输入
            gen_inputs = inputs.copy()
            gen_inputs.update(current_chapter_context) # 更新为当前章节的上下文
            gen_inputs["local_outline"] = next_outline
            gen_inputs["previous_content"] = previous_content
            
            # 重试机制
            chapter_content = ""
            for retry in range(3):
                try:
                    chapter_content = self.novel_generator.invoke(gen_inputs)
                    break
                except OutputParserException as e:
                    if retry == 2:
                        print(f"章节{i}生成失败: {e}")
                        if status_callback:
                            status_callback(f"❌ 第 {i}/{total_chapters} 章生成失败")
                        chapter_content = ""
                    else:
                        if status_callback:
                            status_callback(f"⚠️ 第 {i}/{total_chapters} 章：重试中... ({retry+1}/3)")
                    continue
                except Exception as e:
                    print(f"生成异常: {e}")
                    if retry == 2:
                       chapter_content = "" # Fail gracefully
            
            # 更新本章生成的内容用于下一章的缩写输入（虽然shorter用的是res_content，即上一章的完整内容）
            # 注意：res_content 在循环中被用作"current_content"给shorter，应该是"上一章生成的完整内容"
            # 所以这里我们需要保存这一章的内容给下一轮使用
            res_content = chapter_content
            
            if progress_callback:
                progress_callback((base_progress + progress_per_chapter) / 100)
            
            if chapter_content and status_callback:
                status_callback(f"✅ 第 {i}/{total_chapters} 章完成 ({len(chapter_content)} 字)")
            
            yield chapter_content
