"""Classifier package

Exposes rule-based intent classification utilities alongside the
existing simple English command classifier.
"""

from .ruleStore import RuleStore
from .feedbackEngine import FeedbackEngine
from .intentRouter import IntentRouter

__all__ = ["RuleStore", "FeedbackEngine", "IntentRouter"]


