#pragma once

#include "ApiConfig.h"
#include <memory>
#include <string>
#include <nlohmann/json.hpp>

namespace config {

class ConfigManager {
public:
    explicit ConfigManager(const std::string& config_file_path);
    ~ConfigManager() = default;

    ConfigManager(const ConfigManager&) = delete;
    ConfigManager& operator=(const ConfigManager&) = delete;

    const GlobalConfig& getGlobalConfig() const;

    ApiConfig getApiConfig(const std::string& provider) const;

    std::vector<std::string> getAvailableProviders() const;

    void setApiTimeout(const std::string& provider, int timeout_ms);

    void setMaxTokens(const std::string& provider, int max_tokens);

    void setTemperature(const std::string& provider, double temperature);

    bool hasProvider(const std::string& provider) const;

    void reloadConfig();

    void validateConfig() const;

    std::string getConfigPath() const;

private:
    std::string config_file_path_;
    GlobalConfig global_config_;

    void loadConfig();
    void loadEnvironmentVariables();

    ApiConfig parseApiConfig(const nlohmann::json& json) const;
    AuthConfig parseAuthConfig(const nlohmann::json& json) const;
    EndpointConfig parseEndpointConfig(const nlohmann::json& json) const;
    ConnectionPoolConfig parseConnectionPoolConfig(const nlohmann::json& json) const;
    LoggingConfig parseLoggingConfig(const nlohmann::json& json) const;

    std::string getEnvironmentVariable(const std::string& var_name) const;
};

} // namespace config