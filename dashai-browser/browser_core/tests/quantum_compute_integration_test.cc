#include "base/test/task_environment.h"
#include "dashai-browser/asol/cpp/asol_service_impl.h"
#include "testing/gtest/include/gtest/gtest.h"

namespace dashai_browser {

class QuantumComputeIntegrationTest : public testing::Test {
 protected:
  QuantumComputeIntegrationTest() = default;
  ~QuantumComputeIntegrationTest() override = default;

  void SetUp() override {
    asol_service_ = std::make_unique<asol::ASOLServiceImpl>();
  }

  base::test::TaskEnvironment task_environment_;
  std::unique_ptr<asol::ASOLServiceImpl> asol_service_;
};

TEST_F(QuantumComputeIntegrationTest, RequestQuantumAcceleration) {
  base::RunLoop run_loop;
  asol_service_->RequestQuantumAcceleration(
      mojom::QuantumTaskRequest::New(),
      base::BindOnce(
          [](base::RunLoop* run_loop,
             mojom::QuantumTaskResponsePtr response) {
            EXPECT_TRUE(response->success);
            EXPECT_FALSE(response->classical_fallback_used);
            run_loop->Quit();
          },
          &run_loop));
  run_loop.Run();
}

}  // namespace dashai_browser
