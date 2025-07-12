#include "asol_service_impl.h" // Generally matches the header file name

// For conceptual logging. In a real system, use a proper logging library.
#include <iostream>
#include <sstream> // For string stream formatting
#include <memory>  // For std::make_unique
#include <utility> // For std::move
#include "dashai-browser/asol/core/prompt_generator_client.h"
#include "dashai-browser/asol/core/prompt_feedback_client.h"
#include "dashai-browser/asol/core/echosphere_vcpu_interface.h" // Include the vCPU interface

namespace prometheus_ecosystem {
namespace dashai_browser {
namespace asol {

// Definition for static Status::OK (if not provided by a mock gRPC header)
// This is a simplified stub. In real gRPC, grpc::Status::OK is a predefined constant.
grpc::Status grpc::Status::OK = grpc::Status(true);


// --- StubEchoSphereVCPU (Internal default implementation) ---
// This simple stub will live within the .cc file for now.
class StubEchoSphereVCPU : public core::EchoSphereVCPUInterface {
public:
    StubEchoSphereVCPU() {
        std::cout << "[StubEchoSphereVCPU] Initialized." << std::endl;
    }
    ~StubEchoSphereVCPU() override = default;

    core::ConceptualAiTaskResponse SubmitTask(const core::ConceptualAiTaskRequest& request) override {
        std::cout << "[StubEchoSphereVCPU::SubmitTask] Received Task ID: " << request.task_id
                  << ", Type: " << request.task_type << std::endl;
        core::ConceptualAiTaskResponse response;
        response.task_id = request.task_id;
        response.success = true;
        response.output_data["stub_message"] = "Task processed by StubEchoSphereVCPU.";
        response.output_data["original_task_type"] = request.task_type;
        if (request.task_type == "OPTIMIZE_PROMPT" || request.task_type == "GENERATE_PROMPT") {
            // Simulate vCPU generating/optimizing a prompt string
            response.output_data["final_prompt_string"] = "Generated/Optimized prompt from StubVCPU for task: " + request.task_id;
            response.output_data["generated_by_template_id"] = request.input_data.count("template_id") ? request.input_data.at("template_id") + "_stub_vcpu" : "vcpu_generated";
        }
        response.processed_by_core_id = "stub_core_0";
        response.performance_metrics["processing_time_ms"] = "10";
        return response;
    }

    core::ConceptualVCPUStatusResponse GetVCPUStatus(const core::ConceptualVCPUStatusRequest& request) override {
        std::cout << "[StubEchoSphereVCPU::GetVCPUStatus] Received status request." << std::endl;
        core::ConceptualVCPUStatusResponse response;
        response.overall_status = "OPERATIONAL (Stub)";
        response.core_statuses.push_back({"stub_core_0", "IDLE", 0, 0});
        response.total_pending_tasks = 0;
        response.vcpu_metadata["version"] = "stub_vcpu_v0.1";
        return response;
    }
};
// --- End of StubEchoSphereVCPU ---


AsolServiceImpl::AsolServiceImpl()
    : prompt_generator_client_(std::make_unique<core::PromptGeneratorClient>()),
      prompt_feedback_client_(std::make_unique<core::PromptFeedbackClient>()),
      vcpu_interface_(std::make_unique<StubEchoSphereVCPU>()) { // Initialize vCPU interface with stub
    std::cout << "[AsolServiceImpl] Default constructor: Initialized with stub clients and StubEchoSphereVCPU." << std::endl;
}

// Constructor for injecting a specific vCPU interface (e.g., a mock for testing)
AsolServiceImpl::AsolServiceImpl(std::unique_ptr<core::EchoSphereVCPUInterface> vcpu_interface)
    : prompt_generator_client_(std::make_unique<core::PromptGeneratorClient>()),
      prompt_feedback_client_(std::make_unique<core::PromptFeedbackClient>()),
      vcpu_interface_(std::move(vcpu_interface)) {
    std::cout << "[AsolServiceImpl] Constructor: Initialized with injected EchoSphereVCPUInterface." << std::endl;
}

// Overloaded constructor for injecting all dependencies (primarily for testing)
AsolServiceImpl::AsolServiceImpl(
    std::unique_ptr<core::PromptGeneratorClient> prompt_gen_client,
    std::unique_ptr<core::PromptFeedbackClient> prompt_fb_client,
    std::unique_ptr<core::EchoSphereVCPUInterface> vcpu_interface)
    : prompt_generator_client_(std::move(prompt_gen_client)),
      prompt_feedback_client_(std::move(prompt_fb_client)),
      vcpu_interface_(std::move(vcpu_interface)) {
    std::cout << "[AsolServiceImpl] Constructor: Initialized with all injected dependencies." << std::endl;
}


AsolServiceImpl::~AsolServiceImpl() {}

grpc::Status AsolServiceImpl::GenerateOptimizedPrompt(
    grpc::ServerContext* context,
    const ConceptualPromptGenerationRequest* request,
    ConceptualPromptGenerationResponse* response) {

    std::cout << "[AsolServiceImpl] Received GenerateOptimizedPrompt request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: Request or Response object is null." << std::endl;
        // In real gRPC, you'd return a specific error status like INVALID_ARGUMENT
        // For this conceptual stub, we might just indicate error in the response if possible,
        // or rely on the fact that gRPC framework handles nulls before this point.
        // However, for robustness in the stub:
        if (response) {
            response->error_message = "Internal error: request or response pointer was null.";
        }
        // This conceptual status doesn't have an INTERNAL or INVALID_ARGUMENT, returning OK
        // but the error_message in response should be checked by client.
        return grpc::Status::OK; // Or a conceptual error status if defined
    }

    std::cout << "  Template ID: " << (request->template_id.empty() ? (request->original_prompt_text.empty() ? "[not set]" : "[original text provided]") : request->template_id) << std::endl;
    std::cout << "  Apply Optimization: " << (request->apply_optimization ? "true" : "false") << std::endl;

    // Construct AiTaskRequest
    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_gen_prompt_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = request->apply_optimization ? "OPTIMIZE_PROMPT" : "GENERATE_PROMPT";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::LANGUAGE_MODELER; // Example

    // Populate input_data for the AiTaskRequest
    // This is a simplified mapping. A real implementation might involve more complex serialization.
    if (!request->template_id.empty()) {
        ai_task_request.input_data["template_id"] = request->template_id;
    }
    if (!request->original_prompt_text.empty()) {
        ai_task_request.input_data["original_prompt_text"] = request->original_prompt_text;
    }
    // For simplicity, dynamic_variables and context_modifiers could be JSON strings
    // For now, just passing a count or a primary variable.
    if (!request->dynamic_variables.empty()) {
         // Example: serialize to JSON string or pass key ones
        ai_task_request.input_data["dynamic_variables_count"] = std::to_string(request->dynamic_variables.size());
        if(request->dynamic_variables.count("customer_name"))
            ai_task_request.input_data["customer_name"] = request->dynamic_variables.at("customer_name");
    }
    if (!request->context_modifiers.empty()) {
        ai_task_request.input_data["context_modifiers_count"] = std::to_string(request->context_modifiers.size());
        if(request->context_modifiers.count("tone"))
             ai_task_request.input_data["tone"] = request->context_modifiers.at("tone");
    }
    ai_task_request.input_data["apply_optimization_flag"] = request->apply_optimization ? "true" : "false";


    // Call the vCPU interface
    core::ConceptualAiTaskResponse vcpu_response;
    try {
        vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);

        if (vcpu_response.success) {
            response->final_prompt_string = vcpu_response.output_data.count("final_prompt_string") ? vcpu_response.output_data.at("final_prompt_string") : "Error: Prompt string missing from vCPU response.";
            response->generated_by_template_id = vcpu_response.output_data.count("generated_by_template_id") ? vcpu_response.output_data.at("generated_by_template_id") : request->template_id;
            response->metadata["processed_by_core_id"] = vcpu_response.processed_by_core_id;
            if (vcpu_response.performance_metrics.count("processing_time_ms")) {
                response->metadata["vcpu_processing_time_ms"] = vcpu_response.performance_metrics.at("processing_time_ms");
            }
            response->error_message = "";
        } else {
            response->error_message = "AI-vCPU task failed: " + vcpu_response.error_message;
            std::cerr << "[AsolServiceImpl] AI-vCPU task '" << ai_task_request.task_type << "' failed: " << vcpu_response.error_message << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from EchoSphereVCPUInterface::SubmitTask: " << e.what() << std::endl;
        response->error_message = "Exception occurred while submitting task to AI-vCPU: ";
        response->error_message += e.what();
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from EchoSphereVCPUInterface::SubmitTask." << std::endl;
        response->error_message = "Unknown exception occurred while submitting task to AI-vCPU.";
    }

    std::cout << "[AsolServiceImpl] Sending GenerateOptimizedPrompt response." << std::endl;
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::SubmitPromptFeedback(
    grpc::ServerContext* context,
    const ConceptualPromptFeedbackRequest* request,
    ConceptualPromptFeedbackResponse* response) {

    std::cout << "[AsolServiceImpl] Received SubmitPromptFeedback request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: FeedbackRequest or FeedbackResponse object is null." << std::endl;
        if (response) {
            response->feedback_acknowledged = false;
            response->message = "Internal error: request or response pointer was null.";
        }
        return grpc::Status::OK;
    }

    std::cout << "  Prompt Instance ID: " << request->prompt_instance_id << std::endl;
    std::cout << "  Response Quality Score: " << request->response_quality_score << std::endl;

    // Construct AiTaskRequest for feedback processing
    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_feedback_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "PROCESS_FEEDBACK";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::CONTROL_CORE; // Or LOGIC_PROCESSOR

    ai_task_request.input_data["prompt_instance_id"] = request->prompt_instance_id;
    ai_task_request.input_data["template_id_used"] = request->template_id_used;
    ai_task_request.input_data["response_quality_score"] = std::to_string(request->response_quality_score);
    ai_task_request.input_data["task_success_status"] = request->task_success_status ? "true" : "false"; // Assuming conceptual type has it
    if (!request->user_comment.empty()) {
        ai_task_request.input_data["user_comment"] = request->user_comment;
    }
    // ... (map other PromptFeedbackRequest fields to input_data as needed) ...

    core::ConceptualAiTaskResponse vcpu_response;
    try {
        vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);

        if (vcpu_response.success) {
            response->feedback_acknowledged = true;
            response->message = vcpu_response.output_data.count("acknowledgment_message") ? vcpu_response.output_data.at("acknowledgment_message") : "Feedback processed by AI-vCPU.";
            response->feedback_id = vcpu_response.output_data.count("feedback_processing_id") ? vcpu_response.output_data.at("feedback_processing_id") : request->prompt_instance_id + "_processed";
        } else {
            response->feedback_acknowledged = false;
            response->message = "AI-vCPU feedback processing task failed: " + vcpu_response.error_message;
            std::cerr << "[AsolServiceImpl] AI-vCPU task 'PROCESS_FEEDBACK' failed: " << vcpu_response.error_message << std::endl;
        }

    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from EchoSphereVCPUInterface::SubmitTask for feedback: " << e.what() << std::endl;
        response->feedback_acknowledged = false;
        response->message = "Exception occurred while submitting feedback task to AI-vCPU: ";
        response->message += e.what();
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from EchoSphereVCPUInterface::SubmitTask for feedback." << std::endl;
        response->feedback_acknowledged = false;
        response->message = "Unknown exception occurred while submitting feedback task to AI-vCPU.";
    }

    std::cout << "[AsolServiceImpl] Sending SubmitPromptFeedback response." << std::endl;
    return grpc::Status::OK;
}

// New RPC Implementations
grpc::Status AsolServiceImpl::SubmitAiTask(
    grpc::ServerContext* context,
    const ConceptualAiTaskRequest* request, // These are core::ConceptualAiTaskRequest
    ConceptualAiTaskResponse* response) {

    std::cout << "[AsolServiceImpl] Received SubmitAiTask request for task_type: " << (request ? request->task_type : "null request") << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: AiTaskRequest or AiTaskResponse object is null." << std::endl;
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK; // Or conceptual error
    }

    try {
        *response = vcpu_interface_->SubmitTask(*request);
    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from EchoSphereVCPUInterface::SubmitTask: " << e.what() << std::endl;
        response->success = false;
        response->error_message = "Exception during SubmitTask: ";
        response->error_message += e.what();
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from EchoSphereVCPUInterface::SubmitTask." << std::endl;
        response->success = false;
        response->error_message = "Unknown exception during SubmitTask.";
    }
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::GetVCPUStatus(
    grpc::ServerContext* context,
    const ConceptualVCPUStatusRequest* request,
    ConceptualVCPUStatusResponse* response) {

    std::cout << "[AsolServiceImpl] Received GetVCPUStatus request." << std::endl;
    if (!request || !response) { // request is ConceptualVCPUStatusRequest, response is ConceptualVCPUStatusResponse
        std::cerr << "[AsolServiceImpl] Error: VCPUStatusRequest or VCPUStatusResponse object is null." << std::endl;
        if(response) response->overall_status = "ERROR_NULL_REQUEST_RESPONSE";
        return grpc::Status::OK;
    }

    try {
        // Directly use the conceptual types defined in echosphere_vcpu_interface.h for the vcpu_interface_ call
        core::ConceptualVCPUStatusRequest vcpu_req; // Assuming this maps from the gRPC conceptual type
        vcpu_req.core_ids_filter = request->core_ids_filter; // Direct mapping if structures are identical

        *response = vcpu_interface_->GetVCPUStatus(vcpu_req);
    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from EchoSphereVCPUInterface::GetVCPUStatus: " << e.what() << std::endl;
        response->overall_status = "ERROR_EXCEPTION";
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from EchoSphereVCPUInterface::GetVCPUStatus." << std::endl;
        response->overall_status = "ERROR_UNKNOWN_EXCEPTION";
    }
    return grpc::Status::OK;
}


grpc::Status AsolServiceImpl::GetPageSummary(
    grpc::ServerContext* context,
    const ConceptualPageSummaryRequest* request, // gRPC layer conceptual type
    ConceptualPageSummaryResponse* response) {    // gRPC layer conceptual type

    std::cout << "[AsolServiceImpl] Received GetPageSummary request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: PageSummaryRequest or PageSummaryResponse object is null." << std::endl;
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_get_summary_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "SUMMARIZE_TEXT";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::LANGUAGE_MODELER;

    ai_task_request.input_data["page_content"] = request->page_content_to_summarize;

    switch (request->length_preference) {
        case ConceptualPageSummaryLengthPreference::SHORT:
            ai_task_request.input_data["summary_length"] = "short";
            break;
        case ConceptualPageSummaryLengthPreference::MEDIUM:
            ai_task_request.input_data["summary_length"] = "medium";
            break;
        case ConceptualPageSummaryLengthPreference::DETAILED:
            ai_task_request.input_data["summary_length"] = "detailed";
            break;
        case ConceptualPageSummaryLengthPreference::DEFAULT:
        default:
            ai_task_request.input_data["summary_length"] = "default";
            break;
    }
    if (!request->user_id.empty()) ai_task_request.user_id = request->user_id;
    if (!request->session_id.empty()) ai_task_request.session_id = request->session_id;

    // Add other options from request->options to ai_task_request.input_data
    for(const auto& option_pair : request->options) {
        ai_task_request.input_data[option_pair.first] = option_pair.second;
    }

    std::cout << "[AsolServiceImpl] Submitting SUMMARIZE_TEXT task to AI-vCPU. Content length: "
              << request->page_content_to_summarize.length() << std::endl;

    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);

        if (vcpu_response.success) {
            response->summary_text = vcpu_response.output_data.count("summary_text") ? vcpu_response.output_data.at("summary_text") : "Error: Summary not found in vCPU response.";
            response->error_message = "";
            // Copy any relevant metadata from vcpu_response.performance_metrics or vcpu_response.output_data
            if (vcpu_response.output_data.count("source_language")) {
                response->metadata["source_language"] = vcpu_response.output_data.at("source_language");
            }
            if (vcpu_response.performance_metrics.count("processing_time_ms")) {
                response->metadata["vcpu_processing_time_ms"] = vcpu_response.performance_metrics.at("processing_time_ms");
            }
        } else {
            response->summary_text = "";
            response->error_message = "AI-vCPU summarization task failed: " + vcpu_response.error_message;
            std::cerr << "[AsolServiceImpl] AI-vCPU task 'SUMMARIZE_TEXT' failed: " << vcpu_response.error_message << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from AI-vCPU during summarization: " << e.what() << std::endl;
        response->summary_text = "";
        response->error_message = "Exception occurred during summarization task: ";
        response->error_message += e.what();
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from AI-vCPU during summarization." << std::endl;
        response->summary_text = "";
        response->error_message = "Unknown exception occurred during summarization task.";
    }

    std::cout << "[AsolServiceImpl] Sending GetPageSummary response." << std::endl;
    return grpc::Status::OK;
}


// --- Helper to convert Conceptual enums to string for AI Task ---
std::string WritingAssistanceTypeToString(ConceptualWritingAssistanceTypeProto type) {
    switch (type) {
        case ConceptualWritingAssistanceTypeProto::REPHRASE_GENERAL: return "REPHRASE_GENERAL";
        case ConceptualWritingAssistanceTypeProto::REPHRASE_CASUAL: return "REPHRASE_CASUAL";
        case ConceptualWritingAssistanceTypeProto::REPHRASE_FORMAL: return "REPHRASE_FORMAL";
        case ConceptualWritingAssistanceTypeProto::REPHRASE_CONCISE: return "REPHRASE_CONCISE";
        case ConceptualWritingAssistanceTypeProto::REPHRASE_EXPAND: return "REPHRASE_EXPAND";
        case ConceptualWritingAssistanceTypeProto::CORRECT_GRAMMAR_SPELLING: return "CORRECT_GRAMMAR_SPELLING";
        case ConceptualWritingAssistanceTypeProto::CHANGE_TONE_FRIENDLY: return "CHANGE_TONE_FRIENDLY";
        case ConceptualWritingAssistanceTypeProto::CHANGE_TONE_PROFESSIONAL: return "CHANGE_TONE_PROFESSIONAL";
        case ConceptualWritingAssistanceTypeProto::CHANGE_TONE_PERSUASIVE: return "CHANGE_TONE_PERSUASIVE";
        default: return "UNSPECIFIED_WRITING_ASSISTANCE";
    }
}

std::string CreativeContentTypeToString(ConceptualCreativeContentTypeProto type) {
    switch (type) {
        case ConceptualCreativeContentTypeProto::EMAIL_DRAFT: return "EMAIL_DRAFT";
        case ConceptualCreativeContentTypeProto::SOCIAL_MEDIA_POST_TWITTER: return "SOCIAL_MEDIA_POST_TWITTER";
        case ConceptualCreativeContentTypeProto::SOCIAL_MEDIA_POST_LINKEDIN: return "SOCIAL_MEDIA_POST_LINKEDIN";
        // ... add all other cases
        default: return "UNSPECIFIED_CREATIVE_CONTENT";
    }
}
// --- End Helper ---


grpc::Status AsolServiceImpl::HandleContentCreation(
    grpc::ServerContext* context,
    const ConceptualContentCreationRpcRequest* request,
    ConceptualContentCreationRpcResponse* response) {

    std::cout << "[AsolServiceImpl] Received HandleContentCreation request." << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: ContentCreationRpcRequest or Response object is null." << std::endl;
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_content_creation_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    if(!request->user_id.empty()) ai_task_request.user_id = request->user_id;
    if(!request->session_id.empty()) ai_task_request.session_id = request->session_id;

    bool request_valid = false;

    if (request->active_request_type == ConceptualContentCreationRequestType::WRITING_ASSISTANCE && request->writing_assistance_request) {
        const auto& wa_req = *request->writing_assistance_request;
        ai_task_request.task_type = WritingAssistanceTypeToString(wa_req.options.assistance_type);
        ai_task_request.input_data["selected_text"] = wa_req.selected_text;
        if (!wa_req.options.original_language.empty()) {
            ai_task_request.input_data["original_language"] = wa_req.options.original_language;
        }
        ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::LANGUAGE_MODELER;
        request_valid = true;
        std::cout << "  Type: Writing Assistance (" << ai_task_request.task_type << ")" << std::endl;
    } else if (request->active_request_type == ConceptualContentCreationRequestType::TRANSLATION && request->translation_request) {
        const auto& tr_req = *request->translation_request;
        ai_task_request.task_type = "TRANSLATE_TEXT";
        ai_task_request.input_data["text_to_translate"] = tr_req.text_to_translate;
        ai_task_request.input_data["source_language"] = tr_req.languages.source_language;
        ai_task_request.input_data["target_language"] = tr_req.languages.target_language;
        ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::LANGUAGE_MODELER; // Or a dedicated translation core/API
        request_valid = true;
        std::cout << "  Type: Translation" << std::endl;
    } else if (request->active_request_type == ConceptualContentCreationRequestType::CREATIVE_CONTENT && request->creative_content_request) {
        const auto& cc_req = *request->creative_content_request;
        ai_task_request.task_type = CreativeContentTypeToString(cc_req.options.content_type);
        ai_task_request.input_data["topic_or_brief"] = cc_req.options.topic_or_brief;
        if (cc_req.options.desired_length_words > 0) {
            ai_task_request.input_data["desired_length_words"] = std::to_string(cc_req.options.desired_length_words);
        }
        if (!cc_req.options.desired_tone.empty()) {
            ai_task_request.input_data["desired_tone"] = cc_req.options.desired_tone;
        }
        ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::CREATIVE_GENERATOR;
        request_valid = true;
        std::cout << "  Type: Creative Content (" << ai_task_request.task_type << ")" << std::endl;
    } else {
        response->error_message = "Invalid or unspecified content creation request type.";
        std::cerr << "[AsolServiceImpl] " << response->error_message << std::endl;
        return grpc::Status::OK;
    }

    if (!request_valid) { // Should have been caught by the else above, but as a safeguard.
         response->error_message = "Content creation request was not valid.";
         return grpc::Status::OK;
    }

    std::cout << "[AsolServiceImpl] Submitting task '" << ai_task_request.task_type << "' to AI-vCPU." << std::endl;

    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);
        if (vcpu_response.success) {
            response->resulting_text = vcpu_response.output_data.count("resulting_text") ? vcpu_response.output_data.at("resulting_text") :
                                     (vcpu_response.output_data.count("translated_text") ? vcpu_response.output_data.at("translated_text") :
                                     (vcpu_response.output_data.count("generated_content") ? vcpu_response.output_data.at("generated_content") :
                                     "Error: Expected text output not found in vCPU response."));
            response->error_message = "";
            response->metadata = vcpu_response.performance_metrics; // Or specific metadata
            if (vcpu_response.output_data.count("detected_language")) {
                 response->metadata["detected_language"] = vcpu_response.output_data.at("detected_language");
            }
        } else {
            response->resulting_text = "";
            response->error_message = "AI-vCPU content creation task failed: " + vcpu_response.error_message;
            std::cerr << "[AsolServiceImpl] AI-vCPU task '" << ai_task_request.task_type << "' failed: " << vcpu_response.error_message << std::endl;
        }
    } catch (const std::exception& e) {
        std::cerr << "[AsolServiceImpl] Exception from AI-vCPU during content creation: " << e.what() << std::endl;
        response->resulting_text = "";
        response->error_message = "Exception occurred: ";
        response->error_message += e.what();
    } catch (...) {
        std::cerr << "[AsolServiceImpl] Unknown exception from AI-vCPU during content creation." << std::endl;
        response->resulting_text = "";
        response->error_message = "Unknown exception occurred during content creation task.";
    }

    std::cout << "[AsolServiceImpl] Sending HandleContentCreation response." << std::endl;
    return grpc::Status::OK;
}


// --- Implementations for AI-Enhanced Search & Discovery RPCs ---

grpc::Status AsolServiceImpl::HandleContextualSearch(
    grpc::ServerContext* context,
    const ConceptualContextualSearchRpcRequest* request,
    ConceptualSearchResponseProto* response) {

    std::cout << "[AsolServiceImpl] Received HandleContextualSearch request. Query: " << (request ? request->query : "null") << std::endl;
    if (!request || !response) {
        std::cerr << "[AsolServiceImpl] Error: ContextualSearchRpcRequest or Response object is null." << std::endl;
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_contextual_search_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "CONTEXTUAL_SEARCH";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::LANGUAGE_MODELER; // Could also involve MEMORY_CORE

    ai_task_request.input_data["query"] = request->query;
    if (!request->current_page_content_summary.empty()) {
        ai_task_request.input_data["current_page_context_summary"] = request->current_page_content_summary;
    }
    ai_task_request.input_data["include_history"] = request->options.include_history ? "true" : "false";
    ai_task_request.input_data["include_bookmarks"] = request->options.include_bookmarks ? "true" : "false";
    if (!request->options.current_page_url.empty()) {
        ai_task_request.input_data["current_page_url"] = request->options.current_page_url;
    }
    ai_task_request.input_data["max_results"] = std::to_string(request->options.max_results);
    if (!request->user_id.empty()) ai_task_request.user_id = request->user_id;


    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);
        if (vcpu_response.success) {
            // Assuming vCPU output_data["results_json"] is a JSON string array of SearchResultItemProto-like objects
            // This parsing is conceptual. A real implementation would use a JSON library or structured data.
            if (vcpu_response.output_data.count("results_json")) {
                std::cout << "  Conceptual parsing of results_json from vCPU..." << std::endl;
                // For stub, let's just create one dummy result if the vCPU stub doesn't provide it directly
                ConceptualSearchResultItemProto item;
                item.url = vcpu_response.output_data.count("result_url_0") ? vcpu_response.output_data.at("result_url_0") :"http://example.com/vcpu_search_result";
                item.title = vcpu_response.output_data.count("result_title_0") ? vcpu_response.output_data.at("result_title_0") : "vCPU Search Result for " + request->query;
                item.snippet = vcpu_response.output_data.count("result_snippet_0") ? vcpu_response.output_data.at("result_snippet_0") : "Content from vCPU based on search.";
                item.relevance_score = vcpu_response.output_data.count("result_score_0") ? std::stod(vcpu_response.output_data.at("result_score_0")) : 0.85;
                item.source_type = vcpu_response.output_data.count("result_source_0") ? vcpu_response.output_data.at("result_source_0") : "vcpu_web";
                response->results.push_back(item);
            } else if (vcpu_response.output_data.count("dummy_search_result_title")) { // from StubEchoSphereVCPU
                 ConceptualSearchResultItemProto item;
                 item.title = vcpu_response.output_data.at("dummy_search_result_title");
                 item.url = "http://example.com/stub_vcpu_search";
                 item.snippet = "Stubbed vCPU search result for query: " + request->query;
                 response->results.push_back(item);
            }
            if (vcpu_response.output_data.count("suggested_query_correction")) {
                response->suggested_query_correction = vcpu_response.output_data.at("suggested_query_correction");
            }
            response->error_message = "";
        } else {
            response->error_message = "AI-vCPU contextual search task failed: " + vcpu_response.error_message;
        }
    } catch (const std::exception& e) {
        response->error_message = "Exception during contextual search: " + std::string(e.what());
    }
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::HandleMultimodalSearch(
    grpc::ServerContext* context,
    const ConceptualMultimodalSearchRpcRequest* request,
    ConceptualSearchResponseProto* response) {

    std::cout << "[AsolServiceImpl] Received HandleMultimodalSearch request. Image data size: " << (request ? request->image_data.size() : 0) << std::endl;
    if (!request || !response) {
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_multimodal_search_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "MULTIMODAL_SEARCH";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::VISION_INTERPRETER;

    // image_data would need to be base64 encoded or handled as raw bytes if input_data supported it.
    // For map<string, string>, base64 is typical.
    ai_task_request.input_data["image_data_size"] = std::to_string(request->image_data.size()); // Placeholder
    if(!request->textual_context.empty()) ai_task_request.input_data["textual_context"] = request->textual_context;
    // ... map other options ...
    if (!request->user_id.empty()) ai_task_request.user_id = request->user_id;

    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);
        if (vcpu_response.success) {
            // Similar conceptual parsing of results as in HandleContextualSearch
            if (vcpu_response.output_data.count("results_json")) {
                // ... parse JSON ...
            } else { // Fallback to simpler mock from vCPU stub
                ConceptualSearchResultItemProto item;
                item.url = "http://example.com/vcpu_image_search_result";
                item.title = "vCPU Image Search Result for context: " + request->textual_context;
                item.snippet = "Content found by vCPU based on image input.";
                item.relevance_score = 0.90;
                item.source_type = "vcpu_image";
                response->results.push_back(item);
            }
            response->error_message = "";
        } else {
            response->error_message = "AI-vCPU multimodal search task failed: " + vcpu_response.error_message;
        }
    } catch (const std::exception& e) {
        response->error_message = "Exception during multimodal search: " + std::string(e.what());
    }
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::GetContentRecommendations(
    grpc::ServerContext* context,
    const ConceptualContentRecommendationsRpcRequest* request,
    ConceptualRecommendationListProto* response) {

    std::cout << "[AsolServiceImpl] Received GetContentRecommendations request for user: " << (request ? request->user_id : "null") << std::endl;
    if (!request || !response) {
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_get_recs_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "GET_RECOMMENDATIONS";
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::MEMORY_CORE; // And/or CONTROL_CORE
    ai_task_request.user_id = request->user_id;

    ai_task_request.input_data["max_recommendations"] = std::to_string(request->options.max_recommendations);
    if(!request->options.current_page_context_summary.empty()) {
        ai_task_request.input_data["current_page_context_summary"] = request->options.current_page_context_summary;
    }
    ai_task_request.input_data["exclude_recently_viewed"] = request->options.exclude_recently_viewed ? "true" : "false";


    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);
        if (vcpu_response.success) {
            // Conceptual parsing
            if (vcpu_response.output_data.count("recommendations_json")) {
                // ... parse ...
            } else { // Fallback to simpler mock
                 ConceptualSearchResultItemProto item1;
                 item1.url = "http://example.com/vcpu_reco1";
                 item1.title = "vCPU Recommendation 1 for " + request->user_id;
                 item1.snippet = "You might like this based on your vCPU profile.";
                 item1.source_type = "vcpu_recommendation";
                 response->recommendations.push_back(item1);
            }
            response->error_message = "";
        } else {
            response->error_message = "AI-vCPU recommendation task failed: " + vcpu_response.error_message;
        }
    } catch (const std::exception& e) {
        response->error_message = "Exception during content recommendations: " + std::string(e.what());
    }
    return grpc::Status::OK;
}

grpc::Status AsolServiceImpl::PredictNextBrowsingStep(
    grpc::ServerContext* context,
    const ConceptualPredictNextBrowsingStepRpcRequest* request,
    ConceptualPredictedNextStepProto* response) {

    std::cout << "[AsolServiceImpl] Received PredictNextBrowsingStep request for URL: " << (request ? request->current_url : "null") << std::endl;
    if (!request || !response) {
        if(response) response->error_message = "Request or Response object is null.";
        return grpc::Status::OK;
    }

    core::ConceptualAiTaskRequest ai_task_request;
    ai_task_request.task_id = "asol_predict_next_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count());
    ai_task_request.task_type = "PREDICT_NEXT_STEP";
    // This would map to a TIF_CORE or similar if we had it in AiCoreSpecialization
    ai_task_request.required_specialization = core::ConceptualAiCoreSpecialization::CONTROL_CORE; // Placeholder
    ai_task_request.user_id = request->user_id;

    ai_task_request.input_data["current_url"] = request->current_url;
    // recent_history_urls would be serialized (e.g., JSON array string)
    ai_task_request.input_data["recent_history_count"] = std::to_string(request->recent_history_urls.size());


    try {
        core::ConceptualAiTaskResponse vcpu_response = vcpu_interface_->SubmitTask(ai_task_request);
        if (vcpu_response.success) {
            response->predicted_url = vcpu_response.output_data.count("predicted_url") ? vcpu_response.output_data.at("predicted_url") : "http://example.com/vcpu_predicted_default";
            response->prediction_reason = vcpu_response.output_data.count("prediction_reason") ? vcpu_response.output_data.at("prediction_reason") : "vCPU based prediction.";
            response->confidence_score = vcpu_response.output_data.count("confidence_score") ? std::stod(vcpu_response.output_data.at("confidence_score")) : 0.65;
            response->error_message = "";
        } else {
            response->error_message = "AI-vCPU prediction task failed: " + vcpu_response.error_message;
        }
    } catch (const std::exception& e) {
        response->error_message = "Exception during next step prediction: " + std::string(e.what());
    }
    return grpc::Status::OK;
}


} // namespace asol
} // namespace dashai_browser
} // namespace prometheus_ecosystem
