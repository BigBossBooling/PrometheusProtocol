#include "dashai-browser/asol/cpp/asol_service_impl.h"

#include <iostream>

namespace dashai_browser {
namespace asol {

ASOLServiceImpl::ASOLServiceImpl() {}

ASOLServiceImpl::~ASOLServiceImpl() {}

grpc::Status ASOLServiceImpl::GenerateOptimizedPrompt(
    grpc::ServerContext* context,
    const PromptGenerationRequest* request,
    PromptGenerationResponse* response) {
  std::cout << "Received GenerateOptimizedPrompt request for template: "
            << request->template_id() << std::endl;
  response->set_prompt_string("This is a dummy prompt.");
  return grpc::Status::OK;
}

grpc::Status ASOLServiceImpl::SubmitPromptFeedback(
    grpc::ServerContext* context,
    const PromptFeedbackRequest* request,
    PromptFeedbackResponse* response) {
  std::cout << "Received SubmitPromptFeedback request for prompt: "
            << request->prompt_id() << std::endl;
  return grpc::Status::OK;
}

}  // namespace asol
}  // namespace dashai_browser
