#include "asol_service_impl.h" // Generally matches the header file name

// For conceptual logging. In a real system, use a proper logging library.
#include <iostream>
#include <sstream> // For string stream formatting
#include <memory>  // For std::make_unique
#include "dashai-browser/asol/core/prompt_generator_client.h"
#include "dashai-browser/asol/core/prompt_feedback_client.h" // Include the feedback client

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {

// Definition for static Status::OK (if not provided by a mock gRPC header)
// This is a simplified stub. In real gRPC, grpc::Status::OK is a predefined constant.
grpc::Status grpc::Status::OK = grpc::Status(true);


AsolServiceImpl::AsolServiceImpl()
    : prompt_generator_client_(std::make_unique<core::PromptGeneratorClient>()),
      prompt_feedback_client_(std::make_unique<core::PromptFeedbackClient>()) { // Initialize feedback client
    std::cout << "[AsolServiceImpl] Initialized with PromptGeneratorClient and PromptFeedbackClient." << std::endl;
}

AsolServiceImpl::~AsolServiceImpl() {}

grpc::Status AsolServiceImpl::GenerateOptimizedPrompt(
    grpc::ServerContext* context,
    const ConceptualPromptGenerationRequest* request,
    ConceptualPromptGenerationResponse* response) {

    std::cout << "[AsolServiceImpl] Received GenerateOptimizedPrompt request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: Request or Response object is null." << std::endl;
        // In real gRPC, you'd return a specific error status like INVALID_ARGUMENT
        // For this conceptual stub, we might just indicate error in the response if possible,
        // or rely on the fact that gRPC framework handles nulls before this point.
        // However, for robustness in the stub:
        if (response) {
            response->error_message = "Internal error: request or response pointer was null.";
        }
        // This conceptual status doesn't have an INTERNAL or INVALID_ARGUMENT, returning OK
        // but the error_message in response should be checked by client.
        return grpc::Status::OK; // Or a conceptual error status if defined
    }

    std::cout << "  Template ID: " << (request->template_id.empty() ? "[not set]" : request->template_id) << std::endl;
    std::cout << "  Apply Optimization: " << (request->apply_optimization ? "true" : "false") << std::endl;

    // Call the PromptGeneratorClient
    core::ConceptualPromptGenerationResponse client_response;
    try {
        client_response = prompt_generator_client_->Generate(*request);

        // Populate the RPC response from the client's response
        response->final_prompt_string = client_response.final_prompt_string;
        response->generated_by_template_id = client_response.generated_by_template_id;
        response->error_message = client_response.error_message;
        response->metadata = client_response.metadata;

        if (!client_response.error_message.empty()) {
            std::cout << "[AsolServiceImpl] PromptGeneratorClient returned an error: " << client_response.error_message << std::endl;
            // No specific gRPC error status to return here in stub, error is in message.
        }

    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from PromptGeneratorClient: " << e.what() << std::endl;
        response->error_message = "Exception occurred while calling PromptGeneratorClient: ";
        response->error_message += e.what();
        // return grpc::Status(grpc::StatusCode::INTERNAL, response->error_message); // If real gRPC
        return grpc::Status::OK; // Conceptual: error passed in message
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from PromptGeneratorClient." << std::endl;
        response->error_message = "Unknown exception occurred while calling PromptGeneratorClient.";
        // return grpc::Status(grpc::StatusCode::INTERNAL, response->error_message); // If real gRPC
        return grpc::Status::OK; // Conceptual: error passed in message
    }

    std::cout << "[AsolServiceImpl] Sending GenerateOptimizedPrompt response." << std::endl;
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::SubmitPromptFeedback(
    grpc::ServerContext* context,
    const ConceptualPromptFeedbackRequest* request,
    ConceptualPromptFeedbackResponse* response) {

    std::cout << "[AsolServiceImpl] Received SubmitPromptFeedback request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: FeedbackRequest or FeedbackResponse object is null." << std::endl;
        if (response) {
            response->feedback_acknowledged = false;
            response->message = "Internal error: request or response pointer was null.";
        }
        return grpc::Status::OK; // Or conceptual error
    }

    std::cout << "  Prompt Instance ID: " << request->prompt_instance_id << std::endl;
    std::cout << "  Response Quality Score: " << request->response_quality_score << std::endl;

    // Call the PromptFeedbackClient
    core::ConceptualPromptFeedbackResponse client_response;
    try {
        client_response = prompt_feedback_client_->Submit(*request);

        // Populate the RPC response from the client's response
        response->feedback_acknowledged = client_response.feedback_acknowledged;
        response->message = client_response.message;
        response->feedback_id = client_response.feedback_id;

        if (!client_response.feedback_acknowledged) {
            std::cout << "[AsolServiceImpl] PromptFeedbackClient indicated feedback was not acknowledged (or error)." << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from PromptFeedbackClient: " << e.what() << std::endl;
        response->feedback_acknowledged = false;
        response->message = "Exception occurred while calling PromptFeedbackClient: ";
        response->message += e.what();
        return grpc::Status::OK; // Conceptual: error passed in message
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from PromptFeedbackClient." << std::endl;
        response->feedback_acknowledged = false;
        response->message = "Unknown exception occurred while calling PromptFeedbackClient.";
        return grpc::Status::OK; // Conceptual: error passed in message
    }

    std::cout << "[AsolServiceImpl] Sending SubmitPromptFeedback response." << std::endl;
    return grpc::Status::OK;
}

} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem
