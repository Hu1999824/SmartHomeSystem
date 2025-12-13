import json
import os
from typing import Dict, List


DEFAULT_PATH = "./data/intentRules.json"


class RuleStore:
    def __init__(self, path: str = DEFAULT_PATH):
        self.path = path
        self.rules: Dict[str, List[str]] = {
            "turn_on": ["开", "打开", "开启", "亮", "turn on", "switch on"],
            "turn_off": ["关", "关闭", "灭", "turn off", "switch off"],
            "query_status": ["状态", "怎么样", "是否", "现在", "query", "status"],
        }
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    self.rules.update(data)

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.rules, f, ensure_ascii=False, indent=2)

    def add_keyword(self, intent_key: str, phrase: str) -> None:
        self.rules.setdefault(intent_key, [])
        if phrase not in self.rules[intent_key]:
            self.rules[intent_key].append(phrase)
            self.save()

    def get_keywords(self, intent_key: str) -> List[str]:
        return self.rules.get(intent_key, [])


