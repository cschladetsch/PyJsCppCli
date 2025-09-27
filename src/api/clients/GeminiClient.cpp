#include "GeminiClient.h"
#include "../base/ApiException.h"
#include <nlohmann/json.hpp>
#include <iostream>

namespace api {

GeminiClient::GeminiClient(const config::ApiConfig& config)
    : config_(config), current_model_(config.default_model),
      max_tokens_(config.max_tokens), temperature_(config.temperature), connected_(false) {

    http_client_ = std::make_unique<HttpClient>();
    http_client_->setDefaultTimeout(config_.timeout);
    http_client_->setUserAgent("AI-CLI-Gemini/1.0");

    if (config_.auth.token.empty()) {
        throw ConfigException("Gemini API key not found in environment variable: " + config_.auth.env_var);
    }

    try {
        testConnection();
        connected_ = true;
    } catch (const std::exception& e) {
        std::cerr << "Warning: Failed to test Gemini connection: " << e.what() << std::endl;
        connected_ = false;
    }
}

ApiResponse GeminiClient::sendMessage(const MessageRequest& request) {
    if (!connected_) {
        testConnection();
    }

    auto endpoint_url = buildEndpointUrl("generate");
    endpoint_url = addApiKeyToUrl(endpoint_url);
    auto headers = buildHeaders();
    auto payload = buildGeneratePayload(request);

    try {
        auto http_response = http_client_->post(endpoint_url, payload, headers);
        return parseResponse(http_response);
    } catch (const std::exception& e) {
        throw ApiException("Gemini API request failed: " + std::string(e.what()));
    }
}

std::vector<std::string> GeminiClient::getAvailableModels() {
    std::vector<std::string> models = {
        "gemini-pro",
        "gemini-pro-vision"
    };
    return models;
}

void GeminiClient::setModel(const std::string& model) {
    current_model_ = model;
}

std::string GeminiClient::getCurrentModel() const {
    return current_model_;
}

void GeminiClient::setMaxTokens(int max_tokens) {
    max_tokens_ = max_tokens;
}

void GeminiClient::setTemperature(double temperature) {
    temperature_ = temperature;
}

bool GeminiClient::isConnected() const {
    return connected_;
}

std::string GeminiClient::getProviderName() const {
    return "Google Gemini";
}

void GeminiClient::testConnection() {
    auto endpoint_url = buildEndpointUrl("generate");
    endpoint_url = addApiKeyToUrl(endpoint_url);
    auto headers = buildHeaders();

    // Send a minimal test request
    nlohmann::json test_payload = {
        {"contents", nlohmann::json::array({
            {{"parts", nlohmann::json::array({
                {{"text", "Hi"}}
            })}}
        })}
    };

    try {
        auto http_response = http_client_->post(endpoint_url, test_payload.dump(), headers);
        if (http_response.status_code == 401 || http_response.status_code == 403) {
            throw AuthenticationException("Invalid Gemini API key");
        } else if (http_response.status_code >= 400) {
            throw ConnectionException("Gemini API test failed with status: " + std::to_string(http_response.status_code));
        }
        connected_ = true;
    } catch (const ApiException&) {
        throw;
    } catch (const std::exception& e) {
        throw ConnectionException("Failed to connect to Gemini API: " + std::string(e.what()));
    }
}

std::map<std::string, std::string> GeminiClient::getConnectionInfo() const {
    return {
        {"provider", getProviderName()},
        {"base_url", config_.base_url},
        {"model", current_model_},
        {"connected", connected_ ? "true" : "false"},
        {"max_tokens", std::to_string(max_tokens_)},
        {"temperature", std::to_string(temperature_)}
    };
}

std::string GeminiClient::buildEndpointUrl(const std::string& endpoint) const {
    auto it = config_.endpoints.endpoints.find(endpoint);
    if (it == config_.endpoints.endpoints.end()) {
        throw ConfigException("Endpoint '" + endpoint + "' not found in Gemini configuration");
    }
    return config_.base_url + it->second;
}

std::map<std::string, std::string> GeminiClient::buildHeaders() const {
    std::map<std::string, std::string> headers;
    headers["Content-Type"] = "application/json";
    return headers;
}

std::string GeminiClient::buildGeneratePayload(const MessageRequest& request) const {
    nlohmann::json payload;

    // Gemini uses "contents" array with "parts"
    payload["contents"] = nlohmann::json::array({
        {{"parts", nlohmann::json::array({
            {{"text", request.message}}
        })}}
    });

    // Generation config
    nlohmann::json generation_config;

    if (request.temperature >= 0) {
        generation_config["temperature"] = request.temperature;
    } else {
        generation_config["temperature"] = temperature_;
    }

    if (request.max_tokens > 0) {
        generation_config["maxOutputTokens"] = request.max_tokens;
    } else if (max_tokens_ > 0) {
        generation_config["maxOutputTokens"] = max_tokens_;
    }

    if (!request.stop_sequences.empty()) {
        generation_config["stopSequences"] = request.stop_sequences;
    }

    if (!generation_config.empty()) {
        payload["generationConfig"] = generation_config;
    }

    return payload.dump();
}

ApiResponse GeminiClient::parseResponse(const HttpResponse& http_response) const {
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

        if (json_response.contains("candidates") && json_response["candidates"].is_array() &&
            !json_response["candidates"].empty()) {
            auto first_candidate = json_response["candidates"][0];
            if (first_candidate.contains("content") && first_candidate["content"].contains("parts") &&
                first_candidate["content"]["parts"].is_array() && !first_candidate["content"]["parts"].empty()) {
                auto first_part = first_candidate["content"]["parts"][0];
                if (first_part.contains("text") && first_part["text"].is_string()) {
                    response.content = first_part["text"];
                }
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

std::string GeminiClient::addApiKeyToUrl(const std::string& url) const {
    if (config_.auth.type == "query_param") {
        char separator = (url.find('?') != std::string::npos) ? '&' : '?';
        return url + separator + config_.auth.param_name + "=" + config_.auth.token;
    }
    return url;
}

} // namespace api