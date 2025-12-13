# tools/add_knowledge_tool.py
from langchain_core.tools import Tool
from typing import TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from llm.llmProxy import LLMProxy

def _normalize_relative_time(text: str) -> str:
    """Replace English relative time expressions (e.g., today, tomorrow, day after tomorrow, Monday, next Monday) with concrete dates in YYYY-MM-DD format."""
    now = datetime.now()
    
    # Basic replacements: today, tomorrow, day after tomorrow
    replacements = {
        "today": now.strftime("%Y-%m-%d"),
        "tomorrow": (now + timedelta(days=1)).strftime("%Y-%m-%d"),
        "the day after tomorrow": (now + timedelta(days=2)).strftime("%Y-%m-%d"),
    }

    # Weekday names in English (Monday=0)
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    current_weekday = now.weekday()

    # Handle "Monday", "Tuesday", etc.: default to this week or next week if already passed
    for i, name in enumerate(weekday_names):
        if name.lower() in text.lower():
            days_ahead = i - current_weekday
            if days_ahead < 0:
                days_ahead += 7  # next week's same weekday
            target_date = now + timedelta(days=days_ahead)
            replacements[name] = target_date.strftime("%Y-%m-%d")

    # Handle explicit "next Monday", "next Tuesday", etc.
    for i, name in enumerate(weekday_names):
        next_week_name = f"next {name.lower()}"
        if next_week_name in text.lower():
            days_ahead = i - current_weekday + 7
            target_date = now + timedelta(days=days_ahead)
            # Use original case-matching key for replacement (e.g., "next Monday")
            key = f"next {name}"
            replacements[key] = target_date.strftime("%Y-%m-%d")

    # Perform replacements in a case-insensitive but case-preserving way
    # To keep it simple and safe, we do case-sensitive replacement only for exact matches in `replacements`
    # But ensure longer phrases (e.g., "the day after tomorrow") are replaced before shorter ones ("tomorrow")
    for word in sorted(replacements.keys(), key=len, reverse=True):
        if word in text:
            text = text.replace(word, replacements[word])

    return text

class AddKnowledgeTool:
    def __init__(self, llm_proxy):
        self.llm_proxy = llm_proxy

    def add_knowledge(self, fact: str) -> str:
        if not fact or len(fact.strip()) < 5:
            return "❌ 内容太短，未保存。"

        from langchain_core.documents import Document
        normalized_fact = _normalize_relative_time(fact.strip())
        doc = Document(
            page_content=normalized_fact,
            metadata={
                "source": "user_memory",
                "timestamp": datetime.now().isoformat(),
                "type": "general"
            }
        )
        self.llm_proxy.vector_db.add_documents([doc])
        return "✅ 已将信息存入您的私人知识库。"

    def as_tool(self) -> Tool:
        return Tool(
            name="AddToKnowledgeBase",
            func=self.add_knowledge,
            description=(
                "当用户明确要求记住、记录或存储某条个人信息时使用此工具。"
                "输入必须是一个完整的、可长期保存的事实性陈述句（中文）。"
                "例如：'记住：Wi-Fi密码是12345678' → 输入应为 'Wi-Fi密码是12345678'。"
                "不要包含命令词如'记住'、'记一下'，只提取核心事实。"
            )
        )