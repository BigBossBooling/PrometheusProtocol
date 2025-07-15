package optimizer

import (
	"testing"

	pb "github.com/your-username/prometheus-protocol/proto"
)

func TestOptimizationAgent_Optimize(t *testing.T) {
	oa := New()

	template := &pb.PromptTemplate{
		Id:             "test",
		TemplateString: "Hello",
	}

	feedback := []*pb.OptimizationFeedback{
		{ResponseQualityScore: 0.8},
		{ResponseQualityScore: 0.9},
	}

	optimizedTemplate, err := oa.Optimize(template, feedback)
	if err != nil {
		t.Fatalf("failed to optimize template: %v", err)
	}

	if optimizedTemplate.TemplateString == template.TemplateString {
		t.Errorf("expected template to be optimized, but it was not")
	}
}
