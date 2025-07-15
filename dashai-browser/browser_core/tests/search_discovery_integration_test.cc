#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class SearchDiscoveryIntegrationTest : public testing::Test {
 protected:
  SearchDiscoveryIntegrationTest() = default;
  ~SearchDiscoveryIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(SearchDiscoveryIntegrationTest, RequestContextualSearch) {
  base::RunLoop run_loop;
  asol_service_->RequestContextualSearch(
      "test query", "test context",
      base::BindOnce(
          [](base::RunLoop* run_loop, mojom::SearchResponsePtr response) {
            EXPECT_TRUE(response);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
