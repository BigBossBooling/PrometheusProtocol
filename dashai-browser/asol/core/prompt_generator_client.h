#ifndef PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_GENERATOR_CLIENT_H_
#define PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_GENERATOR_CLIENT_H_

#include "dashai-browser/asol/cpp/asol_service_impl.h" // For ConceptualRequest/Response types
                                                      // In a real setup, this might include the .pb.h directly
                                                      // or a separate file for core data types if ASOL uses its own.

#include <string>
#include <memory> // For std::unique_ptr if needed for pimpl or composition

// Forward declaration of the conceptual response structure, assuming it's defined
// in asol_service_impl.h or a similar accessible header.
// If these were actual .pb.h types, they'd be included directly.
namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
    // These are already defined in asol_service_impl.h as conceptual types.
    // struct ConceptualPromptGenerationRequest;
    // struct ConceptualPromptGenerationResponse;
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem


namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
namespace core { // New namespace for core ASOL components like clients

class PromptGeneratorClient {
public:
    PromptGeneratorClient();
    virtual ~PromptGeneratorClient();

    // Method to generate/optimize a prompt.
    // This is a STUB for now and will return mocked data.
    // It takes the conceptual request type and returns the conceptual response type.
    // Marked as virtual to allow easy mocking in unit tests for AsolServiceImpl.
    virtual ConceptualPromptGenerationResponse Generate(
        const ConceptualPromptGenerationRequest& request);

    // In a real gRPC client, this class would hold a
    // std::unique_ptr<AsolService::StubInterface> stub_;
    // and the Generate method would make an RPC call using this stub.
};

} // namespace core
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem

#endif // PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_GENERATOR_CLIENT_H_
