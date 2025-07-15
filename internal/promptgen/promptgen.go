package promptgen

import (
	"bytes"
	"fmt"
	"text/template"

	pb "github.com/your-username/prometheus-protocol/proto"
)

// PromptGenerator is responsible for generating prompts from templates.
type PromptGenerator struct {
	templates map[string]*template.Template
}

// New creates a new PromptGenerator.
func New() (*PromptGenerator, error) {
	return &PromptGenerator{
		templates: make(map[string]*template.Template),
	}, nil
}

// LoadTemplate loads a prompt template into the generator.
func (g *PromptGenerator) LoadTemplate(id, tmpl string) error {
	t, err := template.New(id).Parse(tmpl)
	if err != nil {
		return err
	}
	g.templates[id] = t
	return nil
}

// Generate generates a prompt from a template.
func (g *PromptGenerator) Generate(req *pb.PromptGenerationRequest) (*pb.GeneratedPrompt, error) {
	t, ok := g.templates[req.TemplateId]
	if !ok {
		return nil, fmt.Errorf("template not found: %s", req.TemplateId)
	}

	// Combine default and request-specific variables.
	vars := make(map[string]string)
	// In a real implementation, we would load the template from a store
	// and get the default context modifiers from there.
	// For now, we'll just use the request's dynamic variables.
	for k, v := range req.DynamicVariables {
		vars[k] = v
	}
	for k, v := range req.ContextModifiers {
		vars[k] = v
	}

	var buf bytes.Buffer
	if err := t.Execute(&buf, vars); err != nil {
		return nil, err
	}

	return &pb.GeneratedPrompt{
		PromptString: buf.String(),
		Metadata:     make(map[string]string), // Placeholder for metadata
	}, nil
}
