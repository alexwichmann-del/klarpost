"""klarpost: policy-as-code for personal email hygiene."""

from klarpost.attention import attention_cost, budget
from klarpost.evaluate import Evaluation, evaluate_message, evaluate_messages
from klarpost.models import Action, Message, PolicyPack, Rule
from klarpost.policy import load_policy, validate_policy
from klarpost.safety import HARD_PROTECTED_CATEGORIES

__all__ = [
    "Action",
    "Evaluation",
    "HARD_PROTECTED_CATEGORIES",
    "Message",
    "PolicyPack",
    "Rule",
    "attention_cost",
    "budget",
    "evaluate_message",
    "evaluate_messages",
    "load_policy",
    "validate_policy",
]

__version__ = "0.1.0"
