#ifndef DASAI_BROWSER_BROWSER_CORE_CHROME_BROWSER_AI_FEATURES_ADAPTIVE_UI_SERVICE_H_
#define DASAI_BROWSER_BROWSER_CORE_CHROME_BROWSER_AI_FEATURES_ADAPTIVE_UI_SERVICE_H_

#include "dashai-browser/browser_core/services/ai_hooks/public/mojom/adaptive_ui.mojom.h"
#include "mojo/public/cpp/bindings/remote.h"

namespace dashai_browser {

class AdaptiveUIService {
 public:
  AdaptiveUIService();
  ~AdaptiveUIService();

  void SubmitUserContext(mojom::UserContextDataPtr data);
  void GetUIAdaptationDirectives(const std::string& user_id,
                                 const std::string& current_context);

 private:
  mojo::Remote<mojom::AdaptiveUI> remote_;
};

}  // namespace dashai_browser

#endif  // DASAI_BROWSER_BROWSER_CORE_CHROME_BROWSER_AI_FEATURES_ADAPTIVE_UI_SERVICE_H_
