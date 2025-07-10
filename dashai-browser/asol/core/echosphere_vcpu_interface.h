#ifndef PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_ECHOSPHERE_VCPU_INTERFACE_H_
#define PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_ECHOSPHERE_VCPU_INTERFACE_H_

#include <string>
#include <vector>
#include <map>
#include <memory> // For std::unique_ptr in implementations

// These conceptual structures mirror the protobuf messages for use in the C++ interface.
// In a real build with compiled protos, we would use the generated C++ classes from the .pb.h file.
// For now, these allow defining the interface contract.

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {
namespace core {

// Mirrored from AiCoreSpecialization enum in .proto
enum class ConceptualAiCoreSpecialization {
    CORE_UNSPECIFIED = 0,
    CONTROL_CORE = 1,
    LANGUAGE_MODELER = 2,
    CREATIVE_GENERATOR = 3,
    LOGIC_PROCESSOR = 4,
    PRIVACY_GUARDIAN = 5,
    FUSION_CORE = 6,
    VISION_INTERPRETER = 7,
    KNOWLEDGE_NAVIGATOR = 8,
    RL_TRAINER = 9,
    NEUROPLASTICITY_ENGINE = 10
};

struct ConceptualAiTaskRequest {
    std::string task_id;
    std::string task_type;
    std::map<std::string, std::string> input_data;
    ConceptualAiCoreSpecialization required_specialization = ConceptualAiCoreSpecialization::CORE_UNSPECIFIED;
    int32_t priority = 0; // Using int32_t to match proto's int32
    std::string user_id;  // Optional
    std::string session_id; // Optional
};

struct ConceptualAiTaskResponse {
    std::string task_id;
    bool success = false;
    std::map<std::string, std::string> output_data;
    std::string processed_by_core_id;
    std::string error_message;
    std::map<std::string, std::string> performance_metrics;
};

struct ConceptualVCPUStatusRequest {
    std::vector<std::string> core_ids_filter;
};

struct ConceptualCoreStatus {
    std::string core_id;
    std::string status; // e.g., "IDLE", "PROCESSING"
    int32_t current_load_percentage = 0;
    int32_t pending_tasks_on_core = 0;
};

struct ConceptualVCPUStatusResponse {
    std::string overall_status; // e.g., "OPERATIONAL"
    std::vector<ConceptualCoreStatus> core_statuses;
    int32_t total_pending_tasks = 0;
    std::map<std::string, std::string> vcpu_metadata;
};


class EchoSphereVCPUInterface {
public:
    virtual ~EchoSphereVCPUInterface() = default;

    // Submits a task to the conceptual AI-vCPU for processing.
    virtual ConceptualAiTaskResponse SubmitTask(const ConceptualAiTaskRequest& request) = 0;

    // Gets the current status of the conceptual AI-vCPU.
    // The request parameter is included for consistency, though it might be empty for a general status query.
    virtual ConceptualVCPUStatusResponse GetVCPUStatus(const ConceptualVCPUStatusRequest& request) = 0;
};

} // namespace core
} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem

#endif // PROMETHEUS_ECOSYSTEM_DASHAI_BROWSER_ASOL_CORE_ECHOSPHERE_VCPU_INTERFACE_H_
