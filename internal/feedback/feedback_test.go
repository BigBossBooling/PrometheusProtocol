package feedback

import (
	"testing"

	"github.com/google/go-cmp/cmp"
	"google.golang.org/protobuf/testing/protocmp"

	pb "github.com/your-username/prometheus-protocol/proto"
)

func TestFeedbackCollector_RecordAndGetFeedback(t *testing.T) {
	fc := New()

	feedback1 := &pb.OptimizationFeedback{PromptId: "prompt1", ResponseQualityScore: 0.8}
	feedback2 := &pb.OptimizationFeedback{PromptId: "prompt1", ResponseQualityScore: 0.9}
	feedback3 := &pb.OptimizationFeedback{PromptId: "prompt2", ResponseQualityScore: 0.7}

	fc.RecordFeedback(feedback1)
	fc.RecordFeedback(feedback2)
	fc.RecordFeedback(feedback3)

	prompt1Feedback, err := fc.GetFeedbackForPrompt("prompt1")
	if err != nil {
		t.Fatalf("failed to get feedback for prompt1: %v", err)
	}

	expectedPrompt1Feedback := []*pb.OptimizationFeedback{feedback1, feedback2}
	if diff := cmp.Diff(expectedPrompt1Feedback, prompt1Feedback, protocmp.Transform()); diff != "" {
		t.Errorf("GetFeedbackForPrompt('prompt1') mismatch (-want +got):\n%s", diff)
	}

	prompt2Feedback, err := fc.GetFeedbackForPrompt("prompt2")
	if err != nil {
		t.Fatalf("failed to get feedback for prompt2: %v", err)
	}

	expectedPrompt2Feedback := []*pb.OptimizationFeedback{feedback3}
	if diff := cmp.Diff(expectedPrompt2Feedback, prompt2Feedback, protocmp.Transform()); diff != "" {
		t.Errorf("GetFeedbackForPrompt('prompt2') mismatch (-want +got):\n%s", diff)
	}
}

func TestFeedbackCollector_GetFeedbackForPrompt_NotFound(t *testing.T) {
	fc := New()

	_, err := fc.GetFeedbackForPrompt("non-existent")
	if err == nil {
		t.Errorf("expected error for non-existent prompt, but got nil")
	}
}
