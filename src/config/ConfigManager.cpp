#include "ConfigManager.h"
#include "../api/base/ApiException.h"
#include <fstream>
#include <iostream>
#include <cstdlib>

namespace config {

ConfigManager::ConfigManager(const std::string& config_file_path)
    : config_file_path_(config_file_path) {
    loadConfig();
    loadEnvironmentVariables();
    validateConfig();
}

const GlobalConfig& ConfigManager::getGlobalConfig() const {
    return global_config_;
}

ApiConfig ConfigManager::getApiConfig(const std::string& provider) const {
    auto it = global_config_.apis.find(provider);
    if (it == global_config_.apis.end()) {
        throw api::ConfigException("Provider '" + provider + "' not found in configuration");
    }
    return it->second;
}

std::vector<std::string> ConfigManager::getAvailableProviders() const {
    std::vector<std::string> providers;
    for (const auto& pair : global_config_.apis) {
        providers.push_back(pair.first);
    }
    return providers;
}

void ConfigManager::setApiTimeout(const std::string& provider, int timeout_ms) {
    auto it = global_config_.apis.find(provider);
    if (it != global_config_.apis.end()) {
        it->second.timeout = timeout_ms;
    } else {
        throw api::ConfigException("Provider '" + provider + "' not found");
    }
}

void ConfigManager::setMaxTokens(const std::string& provider, int max_tokens) {
    auto it = global_config_.apis.find(provider);
    if (it != global_config_.apis.end()) {
        it->second.max_tokens = max_tokens;
    } else {
        throw api::ConfigException("Provider '" + provider + "' not found");
    }
}

void ConfigManager::setTemperature(const std::string& provider, double temperature) {
    auto it = global_config_.apis.find(provider);
    if (it != global_config_.apis.end()) {
        it->second.temperature = temperature;
    } else {
        throw api::ConfigException("Provider '" + provider + "' not found");
    }
}

bool ConfigManager::hasProvider(const std::string& provider) const {
    return global_config_.apis.find(provider) != global_config_.apis.end();
}

void ConfigManager::reloadConfig() {
    loadConfig();
    loadEnvironmentVariables();
    validateConfig();
}

void ConfigManager::validateConfig() const {
    if (global_config_.apis.empty()) {
        throw api::ConfigException("No API providers configured");
    }

    for (const auto& pair : global_config_.apis) {
        const auto& provider = pair.first;
        const auto& config = pair.second;

        if (config.name.empty()) {
            throw api::ConfigException("Provider '" + provider + "' has no name");
        }

        if (config.base_url.empty()) {
            throw api::ConfigException("Provider '" + provider + "' has no base_url");
        }

        if (config.auth.env_var.empty()) {
            throw api::ConfigException("Provider '" + provider + "' has no auth environment variable");
        }

        if (config.auth.token.empty()) {
            std::cerr << "Warning: Provider '" + provider + "' has no auth token loaded from environment variable '" + config.auth.env_var + "'\n";
        }

        if (config.endpoints.endpoints.empty()) {
            std::cerr << "Warning: Provider '" + provider + "' has no endpoints configured\n";
        }
    }
}

std::string ConfigManager::getConfigPath() const {
    return config_file_path_;
}

void ConfigManager::loadConfig() {
    std::ifstream file(config_file_path_);
    if (!file.is_open()) {
        throw api::ConfigException("Failed to open config file: " + config_file_path_);
    }

    nlohmann::json json;
    try {
        file >> json;
    } catch (const nlohmann::json::exception& e) {
        throw api::ConfigException("Failed to parse JSON config: " + std::string(e.what()));
    }

    // Parse APIs
    if (json.contains("apis") && json["apis"].is_object()) {
        for (const auto& item : json["apis"].items()) {
            global_config_.apis[item.key()] = parseApiConfig(item.value());
        }
    }

    // Parse connection pool config
    if (json.contains("connection_pool")) {
        global_config_.connection_pool = parseConnectionPoolConfig(json["connection_pool"]);
    }

    // Parse logging config
    if (json.contains("logging")) {
        global_config_.logging = parseLoggingConfig(json["logging"]);
    }
}

void ConfigManager::loadEnvironmentVariables() {
    for (auto& pair : global_config_.apis) {
        auto& config = pair.second;
        if (!config.auth.env_var.empty()) {
            config.auth.token = getEnvironmentVariable(config.auth.env_var);
        }
    }
}

ApiConfig ConfigManager::parseApiConfig(const nlohmann::json& json) const {
    ApiConfig config;

    if (json.contains("name") && json["name"].is_string()) {
        config.name = json["name"];
    }

    if (json.contains("base_url") && json["base_url"].is_string()) {
        config.base_url = json["base_url"];
    }

    if (json.contains("version") && json["version"].is_string()) {
        config.version = json["version"];
    }

    if (json.contains("endpoints")) {
        config.endpoints = parseEndpointConfig(json["endpoints"]);
    }

    if (json.contains("auth")) {
        config.auth = parseAuthConfig(json["auth"]);
    }

    if (json.contains("default_model") && json["default_model"].is_string()) {
        config.default_model = json["default_model"];
    }

    if (json.contains("max_tokens") && json["max_tokens"].is_number_integer()) {
        config.max_tokens = json["max_tokens"];
    }

    if (json.contains("timeout") && json["timeout"].is_number_integer()) {
        config.timeout = json["timeout"];
    }

    if (json.contains("temperature") && json["temperature"].is_number()) {
        config.temperature = json["temperature"];
    }

    if (json.contains("stop_sequences") && json["stop_sequences"].is_array()) {
        for (const auto& item : json["stop_sequences"]) {
            if (item.is_string()) {
                config.stop_sequences.push_back(item);
            }
        }
    }

    return config;
}

AuthConfig ConfigManager::parseAuthConfig(const nlohmann::json& json) const {
    AuthConfig config;

    if (json.contains("type") && json["type"].is_string()) {
        config.type = json["type"];
    }

    if (json.contains("header_name") && json["header_name"].is_string()) {
        config.header_name = json["header_name"];
    }

    if (json.contains("param_name") && json["param_name"].is_string()) {
        config.param_name = json["param_name"];
    }

    if (json.contains("env_var") && json["env_var"].is_string()) {
        config.env_var = json["env_var"];
    }

    return config;
}

EndpointConfig ConfigManager::parseEndpointConfig(const nlohmann::json& json) const {
    EndpointConfig config;

    if (json.is_object()) {
        for (const auto& item : json.items()) {
            if (item.value().is_string()) {
                config.endpoints[item.key()] = item.value();
            }
        }
    }

    return config;
}

ConnectionPoolConfig ConfigManager::parseConnectionPoolConfig(const nlohmann::json& json) const {
    ConnectionPoolConfig config;

    if (json.contains("max_connections") && json["max_connections"].is_number_integer()) {
        config.max_connections = json["max_connections"];
    }

    if (json.contains("keep_alive") && json["keep_alive"].is_boolean()) {
        config.keep_alive = json["keep_alive"];
    }

    if (json.contains("verify_ssl") && json["verify_ssl"].is_boolean()) {
        config.verify_ssl = json["verify_ssl"];
    }

    if (json.contains("retry_attempts") && json["retry_attempts"].is_number_integer()) {
        config.retry_attempts = json["retry_attempts"];
    }

    if (json.contains("retry_delay") && json["retry_delay"].is_number_integer()) {
        config.retry_delay = json["retry_delay"];
    }

    return config;
}

LoggingConfig ConfigManager::parseLoggingConfig(const nlohmann::json& json) const {
    LoggingConfig config;

    if (json.contains("level") && json["level"].is_string()) {
        config.level = json["level"];
    }

    if (json.contains("log_requests") && json["log_requests"].is_boolean()) {
        config.log_requests = json["log_requests"];
    }

    if (json.contains("log_responses") && json["log_responses"].is_boolean()) {
        config.log_responses = json["log_responses"];
    }

    return config;
}

std::string ConfigManager::getEnvironmentVariable(const std::string& var_name) const {
    const char* value = std::getenv(var_name.c_str());
    return value ? std::string(value) : std::string();
}

} // namespace config