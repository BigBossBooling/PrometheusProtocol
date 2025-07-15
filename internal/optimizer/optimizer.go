package optimizer

import (
	"github.com/your-username/prometheus-protocol/internal/mutator"
	pb "github.com/your-username/prometheus-protocol/proto"
)

// OptimizationAgent is the core intelligence driving prompt optimization.
type OptimizationAgent struct {
	mutator *mutator.PromptMutator
}

// New creates a new OptimizationAgent.
func New() *OptimizationAgent {
	return &OptimizationAgent{
		mutator: mutator.New(),
	}
}

// Optimize optimizes a prompt template based on feedback.
func (a *OptimizationAgent) Optimize(template *pb.PromptTemplate, feedbackHistory []*pb.OptimizationFeedback) (*pb.PromptTemplate, error) {
	// For this prototype, we'll just generate one mutation.
	// A real implementation would involve a more sophisticated
	// selection process based on the feedback history.
	return a.mutator.Mutate(template)
}
