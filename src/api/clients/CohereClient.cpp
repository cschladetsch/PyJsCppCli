#include "CohereClient.h"
#include "../base/ApiException.h"
#include <nlohmann/json.hpp>
#include <iostream>

namespace api {

CohereClient::CohereClient(const config::ApiConfig& config)
    : config_(config), current_model_(config.default_model),
      max_tokens_(config.max_tokens), temperature_(config.temperature), connected_(false) {

    http_client_ = std::make_unique<HttpClient>();
    http_client_->setDefaultTimeout(config_.timeout);
    http_client_->setUserAgent("AI-CLI-Cohere/1.0");

    if (config_.auth.token.empty()) {
        throw ConfigException("Cohere API key not found in environment variable: " + config_.auth.env_var);
    }

    try {
        testConnection();
        connected_ = true;
    } catch (const std::exception& e) {
        std::cerr << "Warning: Failed to test Cohere connection: " << e.what() << std::endl;
        connected_ = false;
    }
}

ApiResponse CohereClient::sendMessage(const MessageRequest& request) {
    if (!connected_) {
        testConnection();
    }

    auto endpoint_url = buildEndpointUrl("chat");
    auto headers = buildHeaders();
    auto payload = buildChatPayload(request);

    try {
        auto http_response = http_client_->post(endpoint_url, payload, headers);
        return parseResponse(http_response);
    } catch (const std::exception& e) {
        throw ApiException("Cohere API request failed: " + std::string(e.what()));
    }
}

std::vector<std::string> CohereClient::getAvailableModels() {
    std::vector<std::string> models = {
        "command",
        "command-r",
        "command-r-plus",
        "command-light"
    };
    return models;
}

void CohereClient::setModel(const std::string& model) {
    current_model_ = model;
}

std::string CohereClient::getCurrentModel() const {
    return current_model_;
}

void CohereClient::setMaxTokens(int max_tokens) {
    max_tokens_ = max_tokens;
}

void CohereClient::setTemperature(double temperature) {
    temperature_ = temperature;
}

bool CohereClient::isConnected() const {
    return connected_;
}

std::string CohereClient::getProviderName() const {
    return "Cohere";
}

void CohereClient::testConnection() {
    auto endpoint_url = buildEndpointUrl("chat");
    auto headers = buildHeaders();

    // Send a minimal test request
    nlohmann::json test_payload = {
        {"model", current_model_},
        {"message", "Hi"},
        {"max_tokens", 1}
    };

    try {
        auto http_response = http_client_->post(endpoint_url, test_payload.dump(), headers);
        if (http_response.status_code == 401) {
            throw AuthenticationException("Invalid Cohere API key");
        } else if (http_response.status_code >= 400) {
            throw ConnectionException("Cohere API test failed with status: " + std::to_string(http_response.status_code));
        }
        connected_ = true;
    } catch (const ApiException&) {
        throw;
    } catch (const std::exception& e) {
        throw ConnectionException("Failed to connect to Cohere API: " + std::string(e.what()));
    }
}

std::map<std::string, std::string> CohereClient::getConnectionInfo() const {
    return {
        {"provider", getProviderName()},
        {"base_url", config_.base_url},
        {"model", current_model_},
        {"connected", connected_ ? "true" : "false"},
        {"max_tokens", std::to_string(max_tokens_)},
        {"temperature", std::to_string(temperature_)}
    };
}

std::string CohereClient::buildEndpointUrl(const std::string& endpoint) const {
    auto it = config_.endpoints.endpoints.find(endpoint);
    if (it == config_.endpoints.endpoints.end()) {
        throw ConfigException("Endpoint '" + endpoint + "' not found in Cohere configuration");
    }
    return config_.base_url + it->second;
}

std::map<std::string, std::string> CohereClient::buildHeaders() const {
    std::map<std::string, std::string> headers;

    headers["Content-Type"] = "application/json";

    if (config_.auth.type == "bearer") {
        headers["Authorization"] = "Bearer " + config_.auth.token;
    }

    return headers;
}

std::string CohereClient::buildChatPayload(const MessageRequest& request) const {
    nlohmann::json payload;

    payload["model"] = request.model.empty() ? current_model_ : request.model;
    payload["message"] = request.message;

    if (request.max_tokens > 0) {
        payload["max_tokens"] = request.max_tokens;
    } else if (max_tokens_ > 0) {
        payload["max_tokens"] = max_tokens_;
    }

    if (request.temperature >= 0) {
        payload["temperature"] = request.temperature;
    } else {
        payload["temperature"] = temperature_;
    }

    if (!request.stop_sequences.empty()) {
        payload["stop_sequences"] = request.stop_sequences;
    }

    return payload.dump();
}

ApiResponse CohereClient::parseResponse(const HttpResponse& http_response) const {
    ApiResponse response;
    response.status_code = http_response.status_code;
    response.headers = http_response.headers;
    response.success = http_response.success;
    response.error_message = http_response.error_message;

    if (!http_response.success) {
        response.content = http_response.body;
        return response;
    }

    try {
        auto json_response = nlohmann::json::parse(http_response.body);

        if (json_response.contains("text") && json_response["text"].is_string()) {
            response.content = json_response["text"];
        } else {
            response.content = "No content in response";
            response.success = false;
        }
    } catch (const nlohmann::json::exception& e) {
        response.content = "Failed to parse response: " + std::string(e.what());
        response.success = false;
    }

    return response;
}

} // namespace api