package main

import (
	"context"
	"fmt"
	"log"
	"net"

	"google.golang.org/grpc"

	"github.com/your-username/prometheus-protocol/internal/promptgen"
	pb "github.com/your-username/prometheus-protocol/proto"
)

type server struct {
	pb.UnimplementedPromptServiceServer
	promptGenerator *promptgen.PromptGenerator
}

func (s *server) GeneratePrompt(ctx context.Context, req *pb.PromptGenerationRequest) (*pb.GeneratedPrompt, error) {
	return s.promptGenerator.Generate(req)
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

	pb.RegisterPromptServiceServer(s, &server{promptGenerator: pg})

	fmt.Println("Server listening on port 50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}
