package mutator

import (
	"math/rand"

	pb "github.com/your-username/prometheus-protocol/proto"
)

// PromptMutator is responsible for generating variations of prompt templates.
type PromptMutator struct{}

// New creates a new PromptMutator.
func New() *PromptMutator {
	return &PromptMutator{}
}

// Mutate generates a variation of a prompt template.
func (m *PromptMutator) Mutate(template *pb.PromptTemplate) (*pb.PromptTemplate, error) {
	newTemplate := &pb.PromptTemplate{
		Id:                      template.Id,
		TemplateString:          template.TemplateString,
		DefaultContextModifiers: make(map[string]string),
	}

	for k, v := range template.DefaultContextModifiers {
		newTemplate.DefaultContextModifiers[k] = v
	}

	// Simple mutation: randomly add a suffix to the template string.
	suffixes := []string{" in a friendly tone.", " in a professional tone.", " in a casual tone."}
	newTemplate.TemplateString += suffixes[rand.Intn(len(suffixes))]

	return newTemplate, nil
}
