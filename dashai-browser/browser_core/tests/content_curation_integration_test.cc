#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class ContentCurationIntegrationTest : public testing::Test {
 protected:
  ContentCurationIntegrationTest() = default;
  ~ContentCurationIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(ContentCurationIntegrationTest, RequestContentAnalysis) {
  base::RunLoop run_loop;
  asol_service_->RequestContentAnalysis(
      mojom::ContentAnalysisRequest::New(),
      base::BindOnce(
          [](base::RunLoop* run_loop,
             mojom::ContentAnalysisResponsePtr response) {
            EXPECT_TRUE(response);
            EXPECT_EQ(response->integrity_score, 0.8f);
            EXPECT_EQ(response->bias_flags[0], "political");
            EXPECT_EQ(response->suggested_perspectives[0],
                      "https://example.com/perspective");
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

TEST_F(ContentCurationIntegrationTest, SubmitCurationPreferences) {
  base::RunLoop run_loop;
  asol_service_->SubmitCurationPreferences(
      mojom::CurationPreferences::New(),
      base::BindOnce(
          [](base::RunLoop* run_loop, bool success) {
            EXPECT_TRUE(success);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
