#include "prompt_generator_client.h"
#include <iostream> // For conceptual logging
#include <sstream>  // For string manipulation

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
namespace core {

PromptGeneratorClient::PromptGeneratorClient() {
    std::cout << "[PromptGeneratorClient] Stubbed client initialized." << std::endl;
}

PromptGeneratorClient::~PromptGeneratorClient() {
    std::cout << "[PromptGeneratorClient] Stubbed client destroyed." << std::endl;
}

// Stubbed/Mocked implementation of the Generate method
ConceptualPromptGenerationResponse PromptGeneratorClient::Generate(
    const ConceptualPromptGenerationRequest& request) {

    std::cout << "[PromptGeneratorClient::Generate] Received request for template_id: '"
              << (request.template_id.empty() ? request.original_prompt_text.substr(0, 30) + "..." : request.template_id)
              << "', apply_optimization: " << (request.apply_optimization ? "true" : "false")
              << std::endl;

    // Simulate interaction with Prometheus Protocol backend and create a mocked response.
    ConceptualPromptGenerationResponse mock_response;

    // Create a simple mocked prompt string
    std::stringstream ss_prompt;
    ss_prompt << "Mocked prompt for ";
    if (!request.template_id.empty()) {
        ss_prompt << "template '" << request.template_id << "'";
    } else if (!request.original_prompt_text.empty()) {
        ss_prompt << "original text (first 30 chars): '" << request.original_prompt_text.substr(0, 30) << "...'";
    } else {
        ss_prompt << "an unspecified input";
    }

    if (request.dynamic_variables.count("customer_name")) {
        ss_prompt << " with customer_name: " << request.dynamic_variables.at("customer_name");
    } else if (request.dynamic_variables.count("user_name")) {
         ss_prompt << " with user_name: " << request.dynamic_variables.at("user_name");
    }

    mock_response.final_prompt_string = ss_prompt.str();

    if (request.apply_optimization) {
        mock_response.final_prompt_string += " (Optimization conceptually applied by mock client)";
        mock_response.generated_by_template_id = request.template_id + "_mock_optimized_v1";
        mock_response.metadata["optimization_status"] = "MockSuccess";
    } else {
        mock_response.final_prompt_string += " (No optimization requested)";
        mock_response.generated_by_template_id = request.template_id.empty() ? "from_original_text_mock" : request.template_id;
        mock_response.metadata["optimization_status"] = "NotAttempted";
    }

    mock_response.error_message = ""; // No error in this mock successful path

    std::cout << "[PromptGeneratorClient::Generate] Returning mocked response: '"
              << mock_response.final_prompt_string.substr(0, 70) << "...'" << std::endl;

    return mock_response;
}

} // namespace core
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem
