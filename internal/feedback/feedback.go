package feedback

import (
	"fmt"
	"sync"

	pb "github.com/your-username/prometheus-protocol/proto"
)

// FeedbackCollector is responsible for collecting and storing feedback.
type FeedbackCollector struct {
	mu       sync.RWMutex
	feedback map[string][]*pb.OptimizationFeedback
}

// New creates a new FeedbackCollector.
func New() *FeedbackCollector {
	return &FeedbackCollector{
		feedback: make(map[string][]*pb.OptimizationFeedback),
	}
}

// RecordFeedback records feedback for a prompt.
func (c *FeedbackCollector) RecordFeedback(feedback *pb.OptimizationFeedback) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.feedback[feedback.PromptId] = append(c.feedback[feedback.PromptId], feedback)
	return nil
}

// GetFeedbackForPrompt retrieves the feedback history for a prompt.
func (c *FeedbackCollector) GetFeedbackForPrompt(promptID string) ([]*pb.OptimizationFeedback, error) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	feedback, ok := c.feedback[promptID]
	if !ok {
		return nil, fmt.Errorf("no feedback found for prompt %s", promptID)
	}
	return feedback, nil
}
