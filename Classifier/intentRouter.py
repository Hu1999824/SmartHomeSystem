from typing import Literal, Tuple, Optional

from .ruleStore import RuleStore
from .feedbackEngine import FeedbackEngine
from .task_classifier import is_simple_task, execute_simple_task


IntentKey = Literal["turn_on", "turn_off", "query_status", "complex"]


class IntentRouter:
    def __init__(self):
        self.rules = RuleStore()
        self.feedback = FeedbackEngine()

    def classify(self, user_input: str) -> Tuple[IntentKey, Optional[str]]:
        text = (user_input or "").strip()
        low = text.lower()

        for intent_key in ["turn_on", "turn_off", "query_status"]:
            if any(k in text or k in low for k in self.rules.get_keywords(intent_key)):
                action_key = intent_key
                return intent_key, action_key

        is_simple, action_key = is_simple_task(low)
        if is_simple and action_key:
            if "on" in action_key:
                return "turn_on", action_key
            if "off" in action_key:
                return "turn_off", action_key
            if "status" in action_key or "query" in action_key:
                return "query_status", action_key
            return "complex", action_key

        return "complex", None

    def maybe_execute_simple(self, action_key: Optional[str]) -> bool:
        if not action_key:
            return False
        execute_simple_task(action_key)
        return True

    def learn_from_feedback(
        self,
        user_input: str,
        predicted: IntentKey,
        actual: IntentKey,
    ) -> None:
        if actual in ("turn_on", "turn_off", "query_status") and user_input:
            self.rules.add_keyword(actual, user_input)
        self.feedback.record(user_input, predicted, actual)


