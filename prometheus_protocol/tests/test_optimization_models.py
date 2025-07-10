import pytest
from dataclasses import is_dataclass, fields
from datetime import datetime, timezone
from prometheus_protocol.core.optimization_models import OptimizationFeedback, PromptOptimizationState

def test_optimization_feedback_is_dataclass():
    assert is_dataclass(OptimizationFeedback)

def test_optimization_feedback_creation_basic():
    ts = datetime.now(timezone.utc)
    feedback = OptimizationFeedback(
        prompt_id="test_prompt_001",
        response_quality_score=0.85,
        timestamp=ts
    )
    assert feedback.prompt_id == "test_prompt_001"
    assert feedback.response_quality_score == 0.85
    assert feedback.timestamp == ts
    assert feedback.user_satisfaction_score is None
    assert feedback.task_success_status is None
    assert feedback.llm_response_id is None
    assert feedback.error_message is None
    assert feedback.feedback_source is None
    assert feedback.context_snapshot is None

def test_optimization_feedback_creation_full():
    ts = datetime.now(timezone.utc)
    context_snap = {"var1": "value1", "user_intent": "query"}
    feedback = OptimizationFeedback(
        prompt_id="test_prompt_002",
        response_quality_score=0.9,
        user_satisfaction_score=1.0,
        task_success_status=True,
        timestamp=ts,
        llm_response_id="resp_xyz789",
        error_message=None,
        feedback_source="user_explicit_rating",
        context_snapshot=context_snap
    )
    assert feedback.prompt_id == "test_prompt_002"
    assert feedback.response_quality_score == 0.9
    assert feedback.user_satisfaction_score == 1.0
    assert feedback.task_success_status is True
    assert feedback.timestamp == ts
    assert feedback.llm_response_id == "resp_xyz789"
    assert feedback.feedback_source == "user_explicit_rating"
    assert feedback.context_snapshot == context_snap

def test_optimization_feedback_default_timestamp():
    feedback = OptimizationFeedback(prompt_id="p1", response_quality_score=0.5)
    assert isinstance(feedback.timestamp, datetime)
    # Check if it's close to now (within a small delta, e.g., 1 second)
    # Both are now offset-aware
    assert (datetime.now(timezone.utc) - feedback.timestamp).total_seconds() < 1

def test_prompt_optimization_state_is_dataclass():
    assert is_dataclass(PromptOptimizationState)

def test_prompt_optimization_state_creation_basic():
    ts = datetime.now(timezone.utc)
    state = PromptOptimizationState(
        prompt_template_id="template_abc",
        current_version_hash="v_hash_1",
        last_optimized_at=ts # Provide specific timestamp
    )
    assert state.prompt_template_id == "template_abc"
    assert state.current_version_hash == "v_hash_1"
    assert state.last_optimized_at == ts
    assert state.performance_history == []
    assert state.optimization_config == {}

def test_prompt_optimization_state_creation_with_config():
    config = {"learning_rate": 0.01, "max_iterations": 100}
    state = PromptOptimizationState(
        prompt_template_id="template_xyz",
        current_version_hash="v_hash_2",
        optimization_config=config
    )
    assert state.optimization_config == config
    assert isinstance(state.last_optimized_at, datetime) # Should use default_factory

def test_prompt_optimization_state_add_feedback():
    state = PromptOptimizationState(prompt_template_id="t1", current_version_hash="v1")
    assert len(state.performance_history) == 0

    ts_before_add = state.last_optimized_at

    feedback1 = OptimizationFeedback(prompt_id="t1", response_quality_score=0.7) # prompt_id matching state's template_id
    state.add_feedback(feedback1)

    assert len(state.performance_history) == 1
    assert state.performance_history[0] == feedback1
    assert state.last_optimized_at > ts_before_add # Timestamp should update

    # Add feedback that could be for a variant, but the add_feedback logic is simple
    feedback2 = OptimizationFeedback(prompt_id="t1_variant_1", response_quality_score=0.9)
    state.add_feedback(feedback2)
    assert len(state.performance_history) == 2
    # Check sorting (most recent first by default from model)
    assert state.performance_history[0].timestamp >= state.performance_history[1].timestamp


def test_prompt_optimization_state_get_average_response_quality():
    state = PromptOptimizationState(prompt_template_id="avg_test", current_version_hash="v_avg")
    assert state.get_average_response_quality() is None # No history

    # Add feedback where prompt_id might match variants or the main ID
    # The current get_average_response_quality in the model averages *all* feedback in history.
    state.add_feedback(OptimizationFeedback(prompt_id="avg_test_v1", response_quality_score=0.6))
    state.add_feedback(OptimizationFeedback(prompt_id="avg_test", response_quality_score=0.8))
    state.add_feedback(OptimizationFeedback(prompt_id="avg_test_v3", response_quality_score=0.7))

    avg_score = state.get_average_response_quality()
    assert avg_score is not None
    assert pytest.approx(avg_score) == (0.6 + 0.8 + 0.7) / 3
