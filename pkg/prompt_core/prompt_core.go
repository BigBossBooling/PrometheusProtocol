package prompt_core

import (
	"context"
	"fmt"

	pb "github.com/your-username/prometheus-protocol/proto"
)

// Server is a placeholder for the prompt core server.
type Server struct{}

// CreatePrompt is a placeholder for creating a new prompt.
func (s *Server) CreatePrompt(ctx context.Context, req *pb.PromptObject) (*pb.PromptObject, error) {
	fmt.Println("Creating prompt:", req.Prompt)
	return req, nil
}
