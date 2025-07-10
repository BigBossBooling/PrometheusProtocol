import pytest
from datetime import datetime, timedelta, timezone # Added timezone
from prometheus_protocol.core.optimization_models import OptimizationFeedback
from prometheus_protocol.core.feedback_collector import FeedbackCollector

@pytest.fixture
def collector():
    """Provides a fresh FeedbackCollector for each test."""
    return FeedbackCollector()

@pytest.fixture
def sample_feedback_list():
    """Provides a list of sample feedback objects."""
    return [
        OptimizationFeedback(
            prompt_id="prompt1",
            response_quality_score=0.8,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=20)
        ),
        OptimizationFeedback(
            prompt_id="prompt1",
            response_quality_score=0.9,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=10) # More recent
        ),
        OptimizationFeedback(
            prompt_id="prompt2",
            response_quality_score=0.7,
            timestamp=datetime.now(timezone.utc) - timedelta(minutes=5)
        ),
    ]

def test_feedback_collector_initialization(collector: FeedbackCollector):
    assert isinstance(collector._feedback_store, dict) # Actually a defaultdict
    assert len(collector.get_all_feedback()) == 0

def test_record_feedback_single_item(collector: FeedbackCollector):
    feedback = OptimizationFeedback(prompt_id="p1", response_quality_score=0.75)
    collector.record_feedback(feedback)

    retrieved = collector.get_feedback_for_prompt("p1")
    assert len(retrieved) == 1
    assert retrieved[0] == feedback

def test_record_feedback_multiple_items_same_prompt_id(collector: FeedbackCollector, sample_feedback_list: list):
    fb1 = sample_feedback_list[0] # score 0.8, older
    fb2 = sample_feedback_list[1] # score 0.9, more recent

    collector.record_feedback(fb1)
    collector.record_feedback(fb2)

    retrieved = collector.get_feedback_for_prompt("prompt1")
    assert len(retrieved) == 2
    # Check sorting by timestamp (most recent first due to sort in record_feedback)
    assert retrieved[0].timestamp > retrieved[1].timestamp
    assert retrieved[0] == fb2
    assert retrieved[1] == fb1

def test_record_feedback_multiple_items_different_prompt_ids(collector: FeedbackCollector, sample_feedback_list: list):
    for fb in sample_feedback_list:
        collector.record_feedback(fb)

    retrieved_p1 = collector.get_feedback_for_prompt("prompt1")
    assert len(retrieved_p1) == 2

    retrieved_p2 = collector.get_feedback_for_prompt("prompt2")
    assert len(retrieved_p2) == 1
    assert retrieved_p2[0] == sample_feedback_list[2]

def test_record_feedback_invalid_type(collector: FeedbackCollector):
    with pytest.raises(TypeError, match="Provided feedback must be an instance of OptimizationFeedback."):
        collector.record_feedback("not_feedback_object") # type: ignore

def test_get_feedback_for_prompt_non_existent(collector: FeedbackCollector):
    retrieved = collector.get_feedback_for_prompt("non_existent_id")
    assert len(retrieved) == 0
    assert isinstance(retrieved, list)

def test_get_all_feedback(collector: FeedbackCollector, sample_feedback_list: list):
    for fb in sample_feedback_list:
        collector.record_feedback(fb)

    all_feedback = collector.get_all_feedback()
    assert len(all_feedback) == 2 # "prompt1" and "prompt2"
    assert "prompt1" in all_feedback
    assert "prompt2" in all_feedback
    assert len(all_feedback["prompt1"]) == 2
    assert len(all_feedback["prompt2"]) == 1

    # Ensure it returns copies
    all_feedback["prompt1"].append(OptimizationFeedback(prompt_id="p1_extra", response_quality_score=0.1)) # type: ignore
    assert len(collector.get_feedback_for_prompt("prompt1")) == 2 # Internal store should be unchanged

def test_clear_feedback_for_prompt(collector: FeedbackCollector, sample_feedback_list: list):
    for fb in sample_feedback_list:
        collector.record_feedback(fb)

    assert len(collector.get_feedback_for_prompt("prompt1")) == 2
    cleared = collector.clear_feedback_for_prompt("prompt1")
    assert cleared is True
    assert len(collector.get_feedback_for_prompt("prompt1")) == 0
    assert len(collector.get_feedback_for_prompt("prompt2")) == 1 # Other prompts unaffected

    cleared_non_existent = collector.clear_feedback_for_prompt("non_existent_id")
    assert cleared_non_existent is False

def test_clear_all_feedback(collector: FeedbackCollector, sample_feedback_list: list):
    for fb in sample_feedback_list:
        collector.record_feedback(fb)

    assert len(collector.get_all_feedback()) > 0
    collector.clear_all_feedback()
    assert len(collector.get_all_feedback()) == 0

def test_feedback_order_after_multiple_records(collector: FeedbackCollector):
    t1 = datetime.now(timezone.utc) - timedelta(seconds=30)
    t2 = datetime.now(timezone.utc) - timedelta(seconds=10)
    t3 = datetime.now(timezone.utc) - timedelta(seconds=20)

    fb1 = OptimizationFeedback(prompt_id="order_test", response_quality_score=0.1, timestamp=t1)
    fb2 = OptimizationFeedback(prompt_id="order_test", response_quality_score=0.2, timestamp=t2) # most recent
    fb3 = OptimizationFeedback(prompt_id="order_test", response_quality_score=0.3, timestamp=t3)

    collector.record_feedback(fb1) # Oldest
    collector.record_feedback(fb2) # Newest
    collector.record_feedback(fb3) # Middle

    retrieved = collector.get_feedback_for_prompt("order_test")
    assert len(retrieved) == 3
    assert retrieved[0] == fb2 # fb2 (t2) is most recent
    assert retrieved[1] == fb3 # fb3 (t3) is next
    assert retrieved[2] == fb1 # fb1 (t1) is oldest
    assert retrieved[0].timestamp > retrieved[1].timestamp > retrieved[2].timestamp
