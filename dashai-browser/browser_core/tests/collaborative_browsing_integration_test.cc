#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class CollaborativeBrowsingIntegrationTest : public testing::Test {
 protected:
  CollaborativeBrowsingIntegrationTest() = default;
  ~CollaborativeBrowsingIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(CollaborativeBrowsingIntegrationTest, StartSharedSession) {
  base::RunLoop run_loop;
  asol_service_->StartSharedSession(
      mojom::SessionConfig::New(),
      base::BindOnce(
          [](base::RunLoop* run_loop, const std::string& session_id) {
            EXPECT_FALSE(session_id.empty());
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

TEST_F(CollaborativeBrowsingIntegrationTest, JoinSharedSession) {
  base::RunLoop run_loop;
  asol_service_->JoinSharedSession(
      "test_session_id",
      base::BindOnce(
          [](base::RunLoop* run_loop, bool success) {
            EXPECT_TRUE(success);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
