package mutator

import (
	"testing"

	pb "github.com/your-username/prometheus-protocol/proto"
)

func TestPromptMutator_Mutate(t *testing.T) {
	pm := New()

	template := &pb.PromptTemplate{
		Id:             "test",
		TemplateString: "Hello",
	}

	mutatedTemplate, err := pm.Mutate(template)
	if err != nil {
		t.Fatalf("failed to mutate template: %v", err)
	}

	if mutatedTemplate.TemplateString == template.TemplateString {
		t.Errorf("expected template to be mutated, but it was not")
	}
}
