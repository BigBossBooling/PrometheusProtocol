#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class AdaptiveUIIntegrationTest : public testing::Test {
 protected:
  AdaptiveUIIntegrationTest() = default;
  ~AdaptiveUIIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(AdaptiveUIIntegrationTest, SubmitUserContext) {
  base::RunLoop run_loop;
  asol_service_->SubmitUserContext(
      mojom::UserContextData::New(),
      base::BindOnce(
          [](base::RunLoop* run_loop, bool success) {
            EXPECT_TRUE(success);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

TEST_F(AdaptiveUIIntegrationTest, GetUIAdaptationDirectives) {
  base::RunLoop run_loop;
  asol_service_->GetUIAdaptationDirectives(
      "test_user", "test_context",
      base::BindOnce(
          [](base::RunLoop* run_loop,
             mojom::UIAdaptationDirectivePtr directive) {
            EXPECT_TRUE(directive);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
