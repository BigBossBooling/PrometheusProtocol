package promptgen

import (
	"testing"

	"github.com/google/go-cmp/cmp"
	pb "github.com/your-username/prometheus-protocol/proto"
)

func TestPromptGenerator_Generate(t *testing.T) {
	pg, err := New()
	if err != nil {
		t.Fatalf("failed to create prompt generator: %v", err)
	}

	err = pg.LoadTemplate("hello", "Hello, {{.name}}!")
	if err != nil {
		t.Fatalf("failed to load template: %v", err)
	}

	req := &pb.PromptGenerationRequest{
		TemplateId: "hello",
		DynamicVariables: map[string]string{
			"name": "World",
		},
	}

	res, err := pg.Generate(req)
	if err != nil {
		t.Fatalf("failed to generate prompt: %v", err)
	}

	expected := &pb.GeneratedPrompt{
		PromptString: "Hello, World!",
		Metadata:     make(map[string]string),
	}

	if diff := cmp.Diff(expected, res, cmp.Comparer(func(x, y *pb.GeneratedPrompt) bool {
		return x.PromptString == y.PromptString
	})); diff != "" {
		t.Errorf("Generate() mismatch (-want +got):\n%s", diff)
	}
}

func TestPromptGenerator_Generate_MissingTemplate(t *testing.T) {
	pg, err := New()
	if err != nil {
		t.Fatalf("failed to create prompt generator: %v", err)
	}

	req := &pb.PromptGenerationRequest{
		TemplateId: "non-existent",
	}

	_, err = pg.Generate(req)
	if err == nil {
		t.Errorf("expected error for missing template, but got nil")
	}
}
