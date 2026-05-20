import json
from typing import Optional, List, Dict, Any
from openai import OpenAI
from app.config import get_settings

settings = get_settings()

# DeepSeek client (OpenAI-compatible)
client = OpenAI(
    api_key=settings.deepseek_api_key or "sk-demo",
    base_url=settings.deepseek_base_url,
)

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

# 古诗专用系统提示 — 要求返回结构化JSON
POEM_SYSTEM_PROMPT = """你是"小棘的考古助手"，一位热爱诗词的考古学家。请为小学生推荐一首适合的古诗，并以严格的JSON格式返回。

JSON格式要求：
{
  "title": "诗题",
  "dynasty": "朝代",
  "author": "作者",
  "content": ["诗句1", "诗句2", "诗句3", "诗句4"],
  "explanation": "用孩子的语言解释这首诗的大意，100字以内",
  "appreciation": "简单赏析这首诗好在哪里，80字以内"
}

要求：
- 推荐适合8-12岁小学生的经典古诗
- 优先推荐小学课本中的必背篇目
- 诗句要完整，不要遗漏
- 解释和赏析要用孩子的语言，生动有趣
- 适当融入考古/恐龙相关比喻增加趣味性

返回内容必须是严格有效的JSON，不要包含其他文字。"""


def detect_intent(user_message: str) -> Dict[str, Any]:
    """识别用户意图。"""
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
    except Exception as e:
        print(f"意图识别失败: {e}")
        return {
            "intent": "chat",
            "confidence": 50,
            "explanation": "识别失败，默认闲聊",
            "suggested_response": "你好呀！我是小棘的考古助手，今天想学什么？",
        }


def generate_poem(user_message: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
    """生成古诗推荐，返回结构化数据。"""
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
            max_tokens=1000,
            stream=False,
        )
        
        content = response.choices[0].message.content.strip()
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
        
        if isinstance(poem_data["content"], str):
            poem_data["content"] = poem_data["content"].split("\n")
        
        return {
            "success": True,
            "poem": poem_data,
            "text_response": f"来，让我们一起背诵《{poem_data['title']}》！📜\n\n这是{poem_data['dynasty']}·{poem_data['author']}的作品。"
        }
    except Exception as e:
        print(f"古诗生成失败: {e}")
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
        return {
            "success": True,
            "poem": None,
            "text_response": response.choices[0].message.content.strip()
        }
    except Exception as e:
        print(f"AI对话失败: {e}")
        return {
            "success": False,
            "poem": None,
            "text_response": "哎呀，我的放大镜好像出问题了 🔍\n\n请稍后再试，或者换个问题问我～"
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
