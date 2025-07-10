#ifndef PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_FEEDBACK_CLIENT_H_
#define PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_FEEDBACK_CLIENT_H_

#include "dashai-browser/asol/cpp/asol_service_impl.h" // For ConceptualRequest/Response types
                                                      // In a real setup, this might include the .pb.h directly.
#include <string>
#include <memory> // For std::unique_ptr if used internally

// Assuming ConceptualPromptFeedbackRequest and ConceptualPromptFeedbackResponse
// are defined in asol_service_impl.h or an equivalent accessible header for conceptual types.
// namespace prometheus_ecosystem {
// namespace dashai_browser {
// namespace asol {
//     struct ConceptualPromptFeedbackRequest;
//     struct ConceptualPromptFeedbackResponse;
// } // namespace asol
// } // namespace dashai_browser
// } // namespace prometheus_ecosystem
// These are already available via the include of asol_service_impl.h

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
namespace core { // Consistent namespace with PromptGeneratorClient

class PromptFeedbackClient {
public:
    PromptFeedbackClient();
    virtual ~PromptFeedbackClient();

    // Method to submit feedback.
    // This is a STUB for now and will return a simple acknowledgment.
    // Marked as virtual to allow easy mocking in unit tests for AsolServiceImpl.
    virtual ConceptualPromptFeedbackResponse Submit(
        const ConceptualPromptFeedbackRequest& request);

    // In a real gRPC client, this class would typically hold a
    // std::unique_ptr<ActualPrometheusFeedbackService::StubInterface> feedback_stub_;
    // or use the existing AsolService stub if feedback is routed through it to another backend.
    // For this conceptual client communicating with Prometheus Protocol, it would be
    // a client for a service defined by Prometheus Protocol itself.
};

} // namespace core
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem

#endif // PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_PROMPT_FEEDBACK_CLIENT_H_
