#include "AnthropicClient.h"
#include "../base/ApiException.h"
#include <nlohmann/json.hpp>
#include <iostream>

namespace api {

AnthropicClient::AnthropicClient(const config::ApiConfig& config)
    : config_(config), current_model_(config.default_model),
      max_tokens_(config.max_tokens), temperature_(config.temperature), connected_(false) {

    http_client_ = std::make_unique<HttpClient>();
    http_client_->setDefaultTimeout(config_.timeout);
    http_client_->setUserAgent("AI-CLI-Anthropic/1.0");

    if (config_.auth.token.empty()) {
        throw ConfigException("Anthropic API key not found in environment variable: " + config_.auth.env_var);
    }

    try {
        testConnection();
        connected_ = true;
    } catch (const std::exception& e) {
        std::cerr << "Warning: Failed to test Anthropic connection: " << e.what() << std::endl;
        connected_ = false;
    }
}

ApiResponse AnthropicClient::sendMessage(const MessageRequest& request) {
    if (!connected_) {
        testConnection();
    }

    auto endpoint_url = buildEndpointUrl("messages");
    auto headers = buildHeaders();
    auto payload = buildMessagePayload(request);

    try {
        auto http_response = http_client_->post(endpoint_url, payload, headers);
        return parseResponse(http_response);
    } catch (const std::exception& e) {
        throw ApiException("Anthropic API request failed: " + std::string(e.what()));
    }
}

std::vector<std::string> AnthropicClient::getAvailableModels() {
    std::vector<std::string> models = {
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-2.1",
        "claude-2.0",
        "claude-instant-1.2"
    };
    return models;
}

void AnthropicClient::setModel(const std::string& model) {
    current_model_ = model;
}

std::string AnthropicClient::getCurrentModel() const {
    return current_model_;
}

void AnthropicClient::setMaxTokens(int max_tokens) {
    max_tokens_ = max_tokens;
}

void AnthropicClient::setTemperature(double temperature) {
    temperature_ = temperature;
}

bool AnthropicClient::isConnected() const {
    return connected_;
}

std::string AnthropicClient::getProviderName() const {
    return "Anthropic Claude";
}

void AnthropicClient::testConnection() {
    auto endpoint_url = buildEndpointUrl("messages");
    auto headers = buildHeaders();

    // Send a minimal test request
    nlohmann::json test_payload = {
        {"model", current_model_},
        {"max_tokens", 1},
        {"messages", nlohmann::json::array({
            {{"role", "user"}, {"content", "Hi"}}
        })}
    };

    try {
        auto http_response = http_client_->post(endpoint_url, test_payload.dump(), headers);
        if (http_response.status_code == 401) {
            throw AuthenticationException("Invalid Anthropic API key");
        } else if (http_response.status_code >= 400) {
            throw ConnectionException("Anthropic API test failed with status: " + std::to_string(http_response.status_code));
        }
        connected_ = true;
    } catch (const ApiException&) {
        throw;
    } catch (const std::exception& e) {
        throw ConnectionException("Failed to connect to Anthropic API: " + std::string(e.what()));
    }
}

std::map<std::string, std::string> AnthropicClient::getConnectionInfo() const {
    return {
        {"provider", getProviderName()},
        {"base_url", config_.base_url},
        {"model", current_model_},
        {"connected", connected_ ? "true" : "false"},
        {"max_tokens", std::to_string(max_tokens_)},
        {"temperature", std::to_string(temperature_)}
    };
}

std::string AnthropicClient::buildEndpointUrl(const std::string& endpoint) const {
    auto it = config_.endpoints.endpoints.find(endpoint);
    if (it == config_.endpoints.endpoints.end()) {
        throw ConfigException("Endpoint '" + endpoint + "' not found in Anthropic configuration");
    }
    return config_.base_url + it->second;
}

std::map<std::string, std::string> AnthropicClient::buildHeaders() const {
    std::map<std::string, std::string> headers;

    headers["Content-Type"] = "application/json";
    headers["anthropic-version"] = "2023-06-01";

    if (config_.auth.type == "header") {
        headers[config_.auth.header_name] = config_.auth.token;
    }

    return headers;
}

std::string AnthropicClient::buildMessagePayload(const MessageRequest& request) const {
    nlohmann::json payload;

    payload["model"] = request.model.empty() ? current_model_ : request.model;
    payload["max_tokens"] = request.max_tokens > 0 ? request.max_tokens : max_tokens_;

    if (request.temperature >= 0) {
        payload["temperature"] = request.temperature;
    } else {
        payload["temperature"] = temperature_;
    }

    if (!request.stop_sequences.empty()) {
        payload["stop_sequences"] = request.stop_sequences;
    }

    payload["messages"] = nlohmann::json::array({
        {{"role", "user"}, {"content", request.message}}
    });

    return payload.dump();
}

ApiResponse AnthropicClient::parseResponse(const HttpResponse& http_response) const {
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

        if (json_response.contains("content") && json_response["content"].is_array() &&
            !json_response["content"].empty()) {
            auto first_content = json_response["content"][0];
            if (first_content.contains("text") && first_content["text"].is_string()) {
                response.content = first_content["text"];
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