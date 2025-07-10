#ifndef PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_TESTS_MOCK_ECHOSPHERE_VCPU_H_
#define PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_TESTS_MOCK_ECHOSPHERE_VCPU_H_

#include "dashai-browser/asol/core/echosphere_vcpu_interface.h"
#include <iostream> // For logging mock calls

// Basic mocking without GMock.
// If GMock were available, MOCK_METHOD would be used.

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
namespace tests { // Typically tests reside in their own namespace or directly in the tested one

class MockEchoSphereVCPU : public core::EchoSphereVCPUInterface {
public:
    MockEchoSphereVCPU() = default;
    ~MockEchoSphereVCPU() override = default;

    // --- Mock implementation for SubmitTask ---
    core::ConceptualAiTaskResponse SubmitTask(const core::ConceptualAiTaskRequest& request) override {
        std::cout << "[MockEchoSphereVCPU::SubmitTask] Called with Task ID: " << request.task_id
                  << ", Type: " << request.task_type << std::endl;

        submit_task_called_ = true;
        last_task_request_ = request; // Store the last request for verification

        if (should_throw_on_submit_task_) {
            should_throw_on_submit_task_ = false; // Reset for next call
            throw std::runtime_error(submit_task_throw_message_);
        }
        return next_task_response_;
    }

    // --- Mock implementation for GetVCPUStatus ---
    core::ConceptualVCPUStatusResponse GetVCPUStatus(const core::ConceptualVCPUStatusRequest& request) override {
        std::cout << "[MockEchoSphereVCPU::GetVCPUStatus] Called." << std::endl;
        get_vcpu_status_called_ = true;
        last_status_request_ = request; // Store for verification

        if (should_throw_on_get_status_) {
            should_throw_on_get_status_ = false; // Reset
            throw std::runtime_error(get_status_throw_message_);
        }
        return next_status_response_;
    }

    // --- Helper methods for configuring mock behavior ---
    void SetNextAiTaskResponse(const core::ConceptualAiTaskResponse& response) {
        next_task_response_ = response;
    }

    void SetNextVCPUStatusResponse(const core::ConceptualVCPUStatusResponse& response) {
        next_status_response_ = response;
    }

    void SetSubmitTaskToThrow(const std::string& message = "Mock SubmitTask error") {
        should_throw_on_submit_task_ = true;
        submit_task_throw_message_ = message;
    }

    void SetGetStatusToThrow(const std::string& message = "Mock GetStatus error") {
        should_throw_on_get_status_ = true;
        get_status_throw_message_ = message;
    }

    // --- Helper methods for verifying mock interactions ---
    bool WasSubmitTaskCalled() const { return submit_task_called_; }
    const core::ConceptualAiTaskRequest& GetLastTaskRequest() const { return last_task_request_; }

    bool WasGetVCPUStatusCalled() const { return get_vcpu_status_called_; }
    const core::ConceptualVCPUStatusRequest& GetLastStatusRequest() const { return last_status_request_; }

    void ResetMockState() {
        submit_task_called_ = false;
        get_vcpu_status_called_ = false;
        should_throw_on_submit_task_ = false;
        should_throw_on_get_status_ = false;
        last_task_request_ = {}; // Default construct
        last_status_request_ = {}; // Default construct
        next_task_response_ = {}; // Default construct
        next_status_response_ = {}; // Default construct
    }


private:
    core::ConceptualAiTaskResponse next_task_response_;
    core::ConceptualVCPUStatusResponse next_status_response_;

    core::ConceptualAiTaskRequest last_task_request_;
    core::ConceptualVCPUStatusRequest last_status_request_;

    bool submit_task_called_ = false;
    bool get_vcpu_status_called_ = false;

    bool should_throw_on_submit_task_ = false;
    std::string submit_task_throw_message_;
    bool should_throw_on_get_status_ = false;
    std::string get_status_throw_message_;
};

} // namespace tests
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem

#endif // PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_TESTS_MOCK_ECHOSPHERE_VCPU_H_
