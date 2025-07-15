#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class NeuromorphicModesIntegrationTest : public testing::Test {
 protected:
  NeuromorphicModesIntegrationTest() = default;
  ~NeuromorphicModesIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(NeuromorphicModesIntegrationTest, SubmitPowerState) {
  base::RunLoop run_loop;
  asol_service_->SubmitPowerState(
      mojom::PowerState::ON_BATTERY,
      base::BindOnce(
          [](base::RunLoop* run_loop, bool success) {
            EXPECT_TRUE(success);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

TEST_F(NeuromorphicModesIntegrationTest, RequestNeuromorphicMode) {
  base::RunLoop run_loop;
  asol_service_->RequestNeuromorphicMode(
      mojom::NeuromorphicMode::LOW_POWER_BACKGROUND,
      base::BindOnce(
          [](base::RunLoop* run_loop, bool success) {
            EXPECT_TRUE(success);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
