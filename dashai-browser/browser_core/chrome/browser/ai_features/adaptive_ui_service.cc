#include "dashai-browser/browser_core/chrome/browser/ai_features/adaptive_ui_service.h"

#include "base/functional/bind.h"
#include "base/logging.h"

namespace dashai_browser {

AdaptiveUIService::AdaptiveUIService() = default;

AdaptiveUIService::~AdaptiveUIService() = default;

void AdaptiveUIService::SubmitUserContext(mojom::UserContextDataPtr data) {
  remote_->SubmitUserContext(
      std::move(data),
      base::BindOnce([](bool success) {
        if (!success) {
          LOG(ERROR) << "Failed to submit user context.";
        }
      }));
}

void AdaptiveUIService::GetUIAdaptationDirectives(
    const std::string& user_id,
    const std::string& current_context) {
  remote_->GetUIAdaptationDirectives(
      user_id, current_context,
      base::BindOnce([](mojom::UIAdaptationDirectivePtr directive) {
        // Apply the UI adaptation directives.
      }));
}

}  // namespace dashai_browser
