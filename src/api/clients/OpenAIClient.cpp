#include "OpenAIClient.h"
#include "../base/ApiException.h"
#include <nlohmann/json.hpp>
#include <iostream>

namespace api {

OpenAIClient::OpenAIClient(const config::ApiConfig& config)
    : config_(config), current_model_(config.default_model),
      max_tokens_(config.max_tokens), temperature_(config.temperature), connected_(false) {

    http_client_ = std::make_unique<HttpClient>();
    http_client_->setDefaultTimeout(config_.timeout);
    http_client_->setUserAgent("AI-CLI-OpenAI/1.0");

    if (config_.auth.token.empty()) {
        throw ConfigException("OpenAI API key not found in environment variable: " + config_.auth.env_var);
    }

    try {
        testConnection();
        connected_ = true;
    } catch (const std::exception& e) {
        std::cerr << "Warning: Failed to test OpenAI connection: " << e.what() << std::endl;
        connected_ = false;
    }
}

ApiResponse OpenAIClient::sendMessage(const MessageRequest& request) {
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
        throw ApiException("OpenAI API request failed: " + std::string(e.what()));
    }
}

std::vector<std::string> OpenAIClient::getAvailableModels() {
    std::vector<std::string> models = {
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k"
    };
    return models;
}

void OpenAIClient::setModel(const std::string& model) {
    current_model_ = model;
}

std::string OpenAIClient::getCurrentModel() const {
    return current_model_;
}

void OpenAIClient::setMaxTokens(int max_tokens) {
    max_tokens_ = max_tokens;
}

void OpenAIClient::setTemperature(double temperature) {
    temperature_ = temperature;
}

bool OpenAIClient::isConnected() const {
    return connected_;
}

std::string OpenAIClient::getProviderName() const {
    return "OpenAI";
}

void OpenAIClient::testConnection() {
    auto endpoint_url = buildEndpointUrl("models");
    auto headers = buildHeaders();

    try {
        auto http_response = http_client_->get(endpoint_url, headers);
        if (http_response.status_code == 401) {
            throw AuthenticationException("Invalid OpenAI API key");
        } else if (http_response.status_code >= 400) {
            throw ConnectionException("OpenAI API test failed with status: " + std::to_string(http_response.status_code));
        }
        connected_ = true;
    } catch (const ApiException&) {
        throw;
    } catch (const std::exception& e) {
        throw ConnectionException("Failed to connect to OpenAI API: " + std::string(e.what()));
    }
}

std::map<std::string, std::string> OpenAIClient::getConnectionInfo() const {
    return {
        {"provider", getProviderName()},
        {"base_url", config_.base_url},
        {"model", current_model_},
        {"connected", connected_ ? "true" : "false"},
        {"max_tokens", std::to_string(max_tokens_)},
        {"temperature", std::to_string(temperature_)}
    };
}

std::string OpenAIClient::buildEndpointUrl(const std::string& endpoint) const {
    auto it = config_.endpoints.endpoints.find(endpoint);
    if (it == config_.endpoints.endpoints.end()) {
        throw ConfigException("Endpoint '" + endpoint + "' not found in OpenAI configuration");
    }
    return config_.base_url + it->second;
}

std::map<std::string, std::string> OpenAIClient::buildHeaders() const {
    std::map<std::string, std::string> headers;

    headers["Content-Type"] = "application/json";

    if (config_.auth.type == "bearer") {
        headers["Authorization"] = "Bearer " + config_.auth.token;
    }

    return headers;
}

std::string OpenAIClient::buildChatPayload(const MessageRequest& request) const {
    nlohmann::json payload;

    payload["model"] = request.model.empty() ? current_model_ : request.model;

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
        payload["stop"] = request.stop_sequences;
    }

    payload["messages"] = nlohmann::json::array({
        {{"role", "user"}, {"content", request.message}}
    });

    return payload.dump();
}

ApiResponse OpenAIClient::parseResponse(const HttpResponse& http_response) const {
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

        if (json_response.contains("choices") && json_response["choices"].is_array() &&
            !json_response["choices"].empty()) {
            auto first_choice = json_response["choices"][0];
            if (first_choice.contains("message") && first_choice["message"].contains("content")) {
                response.content = first_choice["message"]["content"];
            }
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