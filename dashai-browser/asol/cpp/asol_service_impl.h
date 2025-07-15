#ifndef DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_
#define DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_

#include "dashai-browser/asol/protos/asol_service.grpc.pb.h"

namespace dashai_browser {
namespace asol {

class ASOLServiceImpl final : public ASOLService::Service {
 public:
  ASOLServiceImpl();
  ~ASOLServiceImpl() override;

  grpc::Status GenerateOptimizedPrompt(
      grpc::ServerContext* context,
      const PromptGenerationRequest* request,
      PromptGenerationResponse* response) override;

  grpc::Status SubmitPromptFeedback(
      grpc::ServerContext* context,
      const PromptFeedbackRequest* request,
      PromptFeedbackResponse* response) override;
};

}  // namespace asol
}  // namespace dashai_browser

#endif  // DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_
