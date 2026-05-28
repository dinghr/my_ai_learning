import json
import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI, APIError
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# DeepSeek client (OpenAI-compatible)
client = OpenAI(
    api_key=settings.deepseek_api_key or "sk-demo",
    base_url=settings.deepseek_base_url,
)
logger.info(f"[AI_INIT] DeepSeek client initialized | model={settings.deepseek_model} | base_url={settings.deepseek_base_url} | api_key_set={bool(settings.deepseek_api_key and settings.deepseek_api_key != 'sk-demo')}")

# 意图识别系统提示
INTENT_SYSTEM_PROMPT = """你是一个教育AI助手，专门帮助小学生学习。请分析用户输入的意图，并返回JSON格式结果。

可识别的意图类型：
- "wrong_question": 用户想录入或分析错题（如"这道题错了"、"帮我看看这道题"、拍照上传题目）
- "poem": 用户想学习古诗/诗词（如"背一首古诗"、"李白写的诗"、"唐诗三百首"）
- "math": 用户想学习数学（如"这道数学题怎么做"、"教我乘法"、"奥数题"）
- "reading": 用户想阅读/朗读（如"读一篇文章"、"童话故事"、"课外阅读推荐"）
- "writing": 用户想练字/写作（如"怎么写好这个字"、"作文怎么写"）
- "english": 用户想学英语（如"这个单词什么意思"、"英语对话"）
- "general": 用户想了解某个知识点（如"恐龙是什么"、"为什么天是蓝的"）
- "chat": 闲聊/打招呼/其他

返回格式（严格JSON）：
{
  "intent": "意图类型",
  "confidence": 85,
  "explanation": "简要说明判断理由",
  "suggested_response": "根据意图给出友好的回应开头"
}
"""

# 对话系统提示
CHAT_SYSTEM_PROMPT = """你是"小棘的考古助手"，一个专为小学生设计的AI学习伙伴。你的风格：

1. **温暖有趣**：像一位耐心的考古学家朋友，用孩子的语言交流
2. **启发引导**：不直接给答案，而是引导孩子思考
3. **知识丰富**：善于用类比和故事讲解知识
4. **积极鼓励**：经常表扬孩子的努力和进步
5. **恐龙主题**：偶尔融入恐龙/考古相关比喻

回答要求：
- 中文回答，语言简单易懂
- 适当使用emoji增加趣味性
- 控制回答长度，适合8-12岁孩子阅读
- 如果是数学题，分步骤讲解
- 如果是古诗，先解释大意再赏析
- 如果是错题，先分析错因再给出类似练习

当前对话中，请先根据用户的意图类型调整回答风格。"""

# 古诗专用系统提示 — 要求返回结构化JSON（含拼音）
POEM_SYSTEM_PROMPT = """你是"小棘的考古助手"，一位热爱诗词的考古学家。请为小学生推荐一首适合的古诗，并以严格的JSON格式返回。

JSON格式要求：
{
  "title": "诗题",
  "dynasty": "朝代",
  "author": "作者",
  "content": [
    [{"hz": "床", "py": "chuáng"}, {"hz": "前", "py": "qián"}, {"hz": "明", "py": "míng"}, {"hz": "月", "py": "yuè"}, {"hz": "光", "py": "guāng"}],
    [{"hz": "疑", "py": "yí"}, {"hz": "是", "py": "shì"}, {"hz": "地", "py": "dì"}, {"hz": "上", "py": "shàng"}, {"hz": "霜", "py": "shuāng"}]
  ],
  "explanation": "用孩子的语言解释这首诗的大意，100字以内",
  "appreciation": "简单赏析这首诗好在哪里，80字以内"
}

要求：
- 推荐适合8-12岁小学生的经典古诗（小学必背篇目优先）
- content 中每个字都要单独标注拼音，注意多音字的正确读音
- 诗句要完整，不要遗漏
- 解释和赏析要用孩子的语言，生动有趣
- 适当融入考古/恐龙相关比喻增加趣味性

返回内容必须是严格有效的JSON，不要包含其他文字。"""


def detect_intent(user_message: str) -> Dict[str, Any]:
    """识别用户意图。"""
    logger.info(f"[INTENT_DETECT] start | message={user_message[:50]}... | model={settings.deepseek_model}")
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"[INTENT_DETECT] raw_response={content[:200]}")
        # 提取JSON部分
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        result = json.loads(content)
        return {
            "intent": result.get("intent", "chat"),
            "confidence": result.get("confidence", 50),
            "explanation": result.get("explanation", ""),
            "suggested_response": result.get("suggested_response", ""),
        }
    except APIError as e:
        logger.error(f"[INTENT_DETECT] APIError | status={e.status_code} | code={e.code} | body={e.body}")
        return {
            "intent": "chat",
            "confidence": 50,
            "explanation": f"API错误: {e.code}",
            "suggested_response": "你好呀！我是小棘的考古助手，今天想学什么？",
        }
    except Exception as e:
        logger.error(f"[INTENT_DETECT] Exception | type={type(e).__name__} | msg={e}")
        return {
            "intent": "chat",
            "confidence": 50,
            "explanation": "识别失败，默认闲聊",
            "suggested_response": "你好呀！我是小棘的考古助手，今天想学什么？",
        }


def generate_poem(user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """生成古诗推荐，返回结构化数据（含拼音）。"""
    logger.info(f"[POEM_GEN] start | message={user_message[:50]}...")
    messages = [{"role": "system", "content": POEM_SYSTEM_PROMPT}]
    
    if history:
        for msg in history[-3:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            temperature=0.8,
            max_tokens=1500,
            stream=False,
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"[POEM_GEN] raw_response={content[:200]}")
        # 提取JSON部分
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        poem_data = json.loads(content)
        
        # 验证必要字段
        required = ["title", "dynasty", "author", "content", "explanation", "appreciation"]
        for field in required:
            if field not in poem_data:
                poem_data[field] = ""
        
        # 兼容旧格式：如果 content 是字符串列表，转换为带拼音的字列表
        content_val = poem_data.get("content", [])
        if content_val and isinstance(content_val[0], str):
            # 旧格式：逐句拆分，给每个字标注基础拼音（简化处理）
            converted = []
            for line in content_val:
                chars = []
                for c in line:
                    chars.append({"hz": c, "py": ""})
                converted.append(chars)
            poem_data["content"] = converted
        
        return {
            "success": True,
            "poem": poem_data,
            "text_response": f"来，让我们一起背诵《{poem_data['title']}》！📜\n\n这是{poem_data['dynasty']}·{poem_data['author']}的作品。"
        }
    except APIError as e:
        logger.error(f"[POEM_GEN] APIError | status={e.status_code} | code={e.code}")
        return {
            "success": False,
            "poem": None,
            "text_response": f"哎呀，我的古籍翻页器卡住了 📜\n\nAPI错误: {e.code}",
        }
    except Exception as e:
        logger.error(f"[POEM_GEN] Exception | type={type(e).__name__} | msg={e}")
        return {
            "success": False,
            "poem": None,
            "text_response": "哎呀，我的古籍翻页器卡住了 📜\n\n请再说一次「教我背古诗」，我换一本诗集试试～"
        }


def chat_with_ai(
    user_message: str,
    history: Optional[List[Dict[str, str]]] = None,
    intent: Optional[str] = None,
) -> Dict[str, Any]:
    """与AI对话，返回回复内容和结构化数据。"""
    logger.info(f"[CHAT_AI] start | intent={intent} | message={user_message[:50]}... | history_len={len(history) if history else 0}")
    
    # 古诗意图：返回结构化数据
    if intent == "poem":
        result = generate_poem(user_message, history)
        return result
    
    # 其他意图：普通对话
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    
    if history:
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
    
    if intent and intent != "chat":
        intent_hints = {
            "wrong_question": "用户似乎在询问一道错题，请帮忙分析错因并给出类似练习题。",
            "math": "用户在问数学题，请分步骤引导思考，不要直接给答案。",
            "reading": "用户想找阅读材料，请推荐适合年龄的短文并给出阅读建议。",
            "writing": "用户在问写字/作文问题，请给出具体的技巧指导和示范。",
            "english": "用户在学英语，请用中英夹杂的方式讲解，适合小学生理解。",
            "general": "用户在提问一个知识点，请用有趣的类比和故事来讲解。",
        }
        hint = intent_hints.get(intent, "")
        if hint:
            messages.append({"role": "system", "content": f"[当前意图: {intent}] {hint}"})
    
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            temperature=0.8,
            max_tokens=1500,
            stream=False,
        )
        content = response.choices[0].message.content.strip()
        logger.info(f"[CHAT_AI] success | response_len={len(content)}")
        return {
            "success": True,
            "poem": None,
            "text_response": content
        }
    except APIError as e:
        logger.error(f"[CHAT_AI] APIError | status={e.status_code} | code={e.code} | body={e.body}")
        return {
            "success": False,
            "poem": None,
            "text_response": f"哎呀，我的放大镜好像出问题了 🔍\n\nAPI错误: {e.code}\n\n请稍后再试，或者换个问题问我～"
        }
    except Exception as e:
        logger.error(f"[CHAT_AI] Exception | type={type(e).__name__} | msg={e}")
        return {
            "success": False,
            "poem": None,
            "text_response": "哎呀，我的放大镜好像出问题了 🔍\n\n请稍后再试，或者换个问题问我～"
        }


# 识字专用系统提示
ENRICH_CHARACTER_PROMPT = """你是一个小学语文教育专家。请为给定的汉字提供详细的学习信息。

返回严格的JSON格式：
{
  "pinyin": "拼音，带声调",
  "radical": "偏旁部首说明，如：虫字旁 · 形声字 · 声旁「胡」表音",
  "words": ["组词1", "组词2"],
  "example": "一个包含该字的例句，适合小学生",
  "brainstorm": ["同偏旁字1", "同偏旁字2", "同偏旁字3", "同偏旁字4", "同偏旁字5"]
}

要求：
- 组词选常用、简单的，适合小学生
- 例句生动有趣，不要太长
- 同偏旁字选常见字
- 返回严格有效的JSON，不要包含其他文字"""

READING_PASSAGE_PROMPT = """你是一位小学语文教育专家，熟悉中国现当代文学经典。请从经典散文、名家名篇中选取或改编一段适合小学生阅读的优美文字。

要求：
1. 文章片段150-250字，语言优美、有画面感、情感真挚
2. 适合小学二年级阅读水平（常用字为主，生僻字标注拼音）
3. 内容可以是：朱自清、老舍、冰心、巴金等大师的经典片段；或关于四季、自然、亲情、童趣的优美散文
4. 让小朋友感受文字之美，积累好词好句
5. 不要基于"生字"来生成，而是直接给出一段完整的经典优美文字

返回严格的JSON格式：
{
  "title": "文章标题",
  "author": "原作者（如：朱自清）",
  "content": [
    {"hz": "春", "py": "chūn"},
    {"hz": "天", "py": "tiān"},
    ...
  ],
  "summary": "这段文字大意，50字以内",
  "highlight_words": ["好词1", "好词2", "好词3"]
}

content 中每个字都要标注拼音。highlight_words 列出文中值得积累的优美词语（3-5个）。
返回严格有效的JSON，不要包含其他文字。"""


def enrich_character(character: str) -> Dict[str, Any]:
    """用 DeepSeek 补全生字信息（拼音、组词、例句等）。"""
    logger.info(f"[ENRICH_CHAR] start | character={character}")
    if not settings.deepseek_api_key or settings.deepseek_api_key == "sk-demo":
        # 开发模式：返回基础数据
        return {
            "pinyin": "pīn",
            "radical": "待补充",
            "words": [f"{character}字"],
            "example": f"这是一个包含「{character}」字的例句。",
            "brainstorm": ["待", "补", "充", "字", "例"]
        }
    
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": ENRICH_CHARACTER_PROMPT},
                {"role": "user", "content": f"请为汉字「{character}」提供学习信息"},
            ],
            temperature=0.5,
            max_tokens=500,
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"[ENRICH_CHAR] raw_response={content[:200]}")
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        data = json.loads(content)
        return {
            "pinyin": data.get("pinyin", ""),
            "radical": data.get("radical", ""),
            "words": data.get("words", []),
            "example": data.get("example", ""),
            "brainstorm": data.get("brainstorm", []),
        }
    except APIError as e:
        logger.error(f"[ENRICH_CHAR] APIError | status={e.status_code} | code={e.code}")
        return {
            "pinyin": "",
            "radical": "",
            "words": [],
            "example": "",
            "brainstorm": [],
        }
    except Exception as e:
        logger.error(f"[ENRICH_CHAR] Exception | type={type(e).__name__} | msg={e}")
        return {
            "pinyin": "",
            "radical": "",
            "words": [],
            "example": "",
            "brainstorm": [],
        }


def generate_reading_passage(theme: str = "随机") -> Dict[str, Any]:
    """用 DeepSeek 生成经典优美阅读片段。"""
    logger.info(f"[READING_GEN] start | theme={theme}")
    if not settings.deepseek_api_key or settings.deepseek_api_key == "sk-demo":
        # 开发模式：返回示例数据（朱自清《春》片段）
        return {
            "title": "春",
            "author": "朱自清",
            "content": [
                {"hz": "桃", "py": "táo"}, {"hz": "树", "py": "shù"}, {"hz": "、", "py": ""},
                {"hz": "杏", "py": "xìng"}, {"hz": "树", "py": "shù"}, {"hz": "、", "py": ""},
                {"hz": "梨", "py": "lí"}, {"hz": "树", "py": "shù"}, {"hz": "，", "py": ""},
                {"hz": "你", "py": "nǐ"}, {"hz": "不", "py": "bù"}, {"hz": "让", "py": "ràng"},
                {"hz": "我", "py": "wǒ"}, {"hz": "，", "py": ""}, {"hz": "我", "py": "wǒ"},
                {"hz": "不", "py": "bù"}, {"hz": "让", "py": "ràng"}, {"hz": "你", "py": "nǐ"},
                {"hz": "，", "py": ""}, {"hz": "都", "py": "dōu"}, {"hz": "开", "py": "kāi"},
                {"hz": "满", "py": "mǎn"}, {"hz": "了", "py": "le"}, {"hz": "花", "py": "huā"},
                {"hz": "赶", "py": "gǎn"}, {"hz": "趟", "py": "tàng"}, {"hz": "儿", "py": "er"},
                {"hz": "。", "py": ""},
            ],
            "summary": "朱自清《春》中的经典片段，描写了春天百花盛开的美丽景象。",
            "highlight_words": ["开满", "赶趟儿"],
        }
    
    try:
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[
                {"role": "system", "content": READING_PASSAGE_PROMPT},
                {"role": "user", "content": f"请生成一段主题为「{theme}」的优美阅读片段。"},
            ],
            temperature=0.8,
            max_tokens=1500,
        )
        
        content = response.choices[0].message.content.strip()
        logger.info(f"[READING_GEN] raw_response={content[:200]}")
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        data = json.loads(content)
        return {
            "title": data.get("title", "短文"),
            "author": data.get("author", ""),
            "content": data.get("content", []),
            "summary": data.get("summary", ""),
            "highlight_words": data.get("highlight_words", []),
        }
    except APIError as e:
        logger.error(f"[READING_GEN] APIError | status={e.status_code} | code={e.code}")
        return {
            "title": "生成失败",
            "author": "",
            "content": [{"hz": "请", "py": "qǐng"}, {"hz": "稍", "py": "shāo"}, {"hz": "后", "py": "hòu"}, {"hz": "再", "py": "zài"}, {"hz": "试", "py": "shì"}],
            "summary": f"生成遇到了问题: {e.code}",
            "highlight_words": [],
        }
    except Exception as e:
        logger.error(f"[READING_GEN] Exception | type={type(e).__name__} | msg={e}")
        return {
            "title": "生成失败",
            "author": "",
            "content": [{"hz": "请", "py": "qǐng"}, {"hz": "稍", "py": "shāo"}, {"hz": "后", "py": "hòu"}, {"hz": "再", "py": "zài"}, {"hz": "试", "py": "shì"}],
            "summary": "生成遇到了问题，请稍后再试。",
            "highlight_words": [],
        }


def get_quick_replies(intent: Optional[str] = None) -> List[Dict[str, str]]:
    """根据意图获取快捷回复建议。"""
    defaults = [
        {"label": "背古诗", "icon": "📜", "prompt": "教我背一首古诗"},
        {"label": "数学题", "icon": "🔢", "prompt": "出一道二年级的数学题"},
        {"label": "讲故事", "icon": "📖", "prompt": "讲一个恐龙的故事"},
        {"label": "为什么", "icon": "❓", "prompt": "为什么天空是蓝色的？"},
    ]
    
    intent_replies = {
        "wrong_question": [
            {"label": "再练一题", "icon": "✏️", "prompt": "给我一道类似的题练习"},
            {"label": "讲知识点", "icon": "📚", "prompt": "这个知识点再讲一遍"},
            {"label": "换种方法", "icon": "🔄", "prompt": "这道题还有其他解法吗"},
        ],
        "poem": [
            {"label": "再背一首", "icon": "📜", "prompt": "再教我一首诗"},
            {"label": "讲作者", "icon": "👤", "prompt": "这个诗人还有什么故事"},
            {"label": "听赏析", "icon": "🎵", "prompt": "这首诗好在哪里"},
        ],
        "math": [
            {"label": "再练一题", "icon": "✏️", "prompt": "给我一道类似的题"},
            {"label": "讲公式", "icon": "📐", "prompt": "这个公式怎么理解"},
            {"label": "生活中的", "icon": "🏠", "prompt": "生活中哪里用到这个知识"},
        ],
    }
    
    return intent_replies.get(intent, defaults)
