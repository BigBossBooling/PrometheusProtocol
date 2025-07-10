from typing import List, Dict, DefaultDict
from collections import defaultdict
from prometheus_protocol.core.optimization_models import OptimizationFeedback
# from threading import Lock # For potential future concurrency

class FeedbackCollector:
    """
    Responsible for receiving, storing, and retrieving OptimizationFeedback.
    For this prototype, feedback is stored in memory.
    """

    def __init__(self):
        self._feedback_store: DefaultDict[str, List[OptimizationFeedback]] = defaultdict(list)
        # self._lock = Lock() # For future thread-safety

    def record_feedback(self, feedback: OptimizationFeedback) -> None:
        """
        Records a piece of optimization feedback.
        """
        if not isinstance(feedback, OptimizationFeedback):
            raise TypeError("Provided feedback must be an instance of OptimizationFeedback.")

        # with self._lock:
        self._feedback_store[feedback.prompt_id].append(feedback)
        self._feedback_store[feedback.prompt_id].sort(key=lambda f: f.timestamp, reverse=True)

    def get_feedback_for_prompt(self, prompt_id: str) -> List[OptimizationFeedback]:
        """
        Retrieves all feedback recorded for a specific prompt_id.
        """
        # with self._lock:
        return list(self._feedback_store.get(prompt_id, []))

    def get_all_feedback(self) -> Dict[str, List[OptimizationFeedback]]:
        """
        Retrieves all feedback stored, organized by prompt_id.
        """
        # with self._lock:
        return {pid: list(flist) for pid, flist in self._feedback_store.items()}

    def clear_feedback_for_prompt(self, prompt_id: str) -> bool:
        """
        Removes all feedback associated with a specific prompt_id.
        """
        # with self._lock:
        if prompt_id in self._feedback_store:
            del self._feedback_store[prompt_id]
            return True
        return False

    def clear_all_feedback(self) -> None:
        """
        Removes all feedback from the store.
        """
        # with self._lock:
        self._feedback_store.clear()
