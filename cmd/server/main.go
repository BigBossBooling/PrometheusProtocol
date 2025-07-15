package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"

	"github.com/your-username/prometheus-protocol/internal/feedback"
	"github.com/your-username/prometheus-protocol/internal/optimizer"
	"github.com/your-username/prometheus-protocol/internal/promptgen"
	pb "github.com/your-username/prometheus-protocol/proto"
)

type server struct {
	pb.UnimplementedPromptServiceServer
	promptGenerator *promptgen.PromptGenerator
	feedbackCollector *feedback.FeedbackCollector
	optimizationAgent *optimizer.OptimizationAgent
}

func (s *server) GeneratePrompt(ctx context.Context, req *pb.PromptGenerationRequest) (*pb.GeneratedPrompt, error) {
	return s.promptGenerator.Generate(req)
}

func (s *server) SubmitFeedback(ctx context.Context, req *pb.OptimizationFeedback) (*pb.SubmitFeedbackResponse, error) {
	err := s.feedbackCollector.RecordFeedback(req)
	if err != nil {
		return nil, err
	}
	return &pb.SubmitFeedbackResponse{}, nil
}

func (s *server) OptimizePrompt(ctx context.Context, req *pb.PromptOptimizationState) (*pb.PromptTemplate, error) {
	// In a real implementation, we would fetch the template from a store.
	// For now, we'll just create a dummy template.
	template := &pb.PromptTemplate{
		Id:             req.PromptTemplateId,
		TemplateString: "Hello, {{.name}}!",
	}
	return s.optimizationAgent.Optimize(template, req.PerformanceHistory)
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	s := grpc.NewServer()
	pg, err := promptgen.New()
	if err != nil {
		log.Fatalf("failed to create prompt generator: %v", err)
	}

	// Load a sample template
	err = pg.LoadTemplate("hello", "Hello, {{.name}}!")
	if err != nil {
		log.Fatalf("failed to load template: %v", err)
	}

	fc := feedback.New()
	oa := optimizer.New()

	pb.RegisterPromptServiceServer(s, &server{
		promptGenerator:   pg,
		feedbackCollector: fc,
		optimizationAgent: oa,
	})

	fmt.Println("Server listening on port 50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
