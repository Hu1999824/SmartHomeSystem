import json
import os
from datetime import datetime
from typing import Literal, Optional, Dict, Any


FeedbackIntent = Literal["turn_on", "turn_off", "query_status", "complex"]
LOG_PATH = "./data/feedbackLog.jsonl"


class FeedbackEngine:
    def __init__(self, log_path: str = LOG_PATH):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def record(
        self,
        user_input: str,
        predicted: FeedbackIntent,
        actual: FeedbackIntent,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        rec = {
            "userInput": user_input,
            "predicted": predicted,
            "actual": actual,
            "timestamp": datetime.now().isoformat(),
            **(extra or {}),
        }

        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


