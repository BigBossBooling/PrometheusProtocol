#ifndef DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_
#define DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_

#include "dashai-browser/asol/protos/asol_service.grpc.pb.h"
#include "dashai-browser/browser_core/services/ai_hooks/public/mojom/adaptive_ui.mojom.h"
#include "dashai-browser/browser_core/services/ai_hooks/public/mojom/collaborative_browsing.mojom.h"
#include "dashai-browser/browser_core/services/ai_hooks/public/mojom/search_discovery.mojom.h"

namespace dashai_browser {
namespace asol {

class ASOLServiceImpl final : public ASOLService::Service,
                              public mojom::SearchDiscovery,
                              public mojom::AdaptiveUI,
                              public mojom::CollaborativeBrowsing {
 public:
  ASOLServiceImpl();
  ~ASOLServiceImpl() override;

  // ASOLService implementation
  grpc::Status GenerateOptimizedPrompt(
      grpc::ServerContext* context,
      const PromptGenerationRequest* request,
      PromptGenerationResponse* response) override;

  grpc::Status SubmitPromptFeedback(
      grpc::ServerContext* context,
      const PromptFeedbackRequest* request,
      PromptFeedbackResponse* response) override;

  // mojom::SearchDiscovery implementation
  void RequestContextualSearch(
      const std::string& query,
      const std::string& current_page_context,
      RequestContextualSearchCallback callback) override;
  void RequestMultimodalSearch(
      const std::vector<uint8_t>& image_data,
      const std::string& context,
      RequestMultimodalSearchCallback callback) override;
  void GetContentRecommendations(
      const std::string& user_id,
      mojom::RecommendationOptionsPtr options,
      GetContentRecommendationsCallback callback) override;
  void PredictNextBrowsingStep(
      const std::string& current_url,
      const std::string& recent_history_summary,
      PredictNextBrowsingStepCallback callback) override;

  // mojom::AdaptiveUI implementation
  void SubmitUserContext(mojom::UserContextDataPtr data,
                         SubmitUserContextCallback callback) override;
  void GetUIAdaptationDirectives(
      const std::string& user_id,
      const std::string& current_context,
      GetUIAdaptationDirectivesCallback callback) override;

  // mojom::CollaborativeBrowsing implementation
  void StartSharedSession(mojom::SessionConfigPtr config,
                          StartSharedSessionCallback callback) override;
  void JoinSharedSession(const std::string& session_id,
                         JoinSharedSessionCallback callback) override;
  void SubmitCollaborativeAction(
      const std::string& session_id,
      mojom::CollaborativeActionPtr action,
      SubmitCollaborativeActionCallback callback) override;
  void GetSessionUpdates(const std::string& session_id,
                         GetSessionUpdatesCallback callback) override;
  void RequestAIMediation(const std::string& session_id,
                          const std::string& context,
                          RequestAIMediationCallback callback) override;
};

}  // namespace asol
}  // namespace dashai_browser

#endif  // DASAI_BROWSER_ASOL_ASOL_SERVICE_IMPL_H_
