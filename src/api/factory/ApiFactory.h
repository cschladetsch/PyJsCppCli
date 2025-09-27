#pragma once

#include "../base/IApiClient.h"
#include "../../config/ConfigManager.h"
#include <memory>
#include <string>
#include <map>
#include <functional>

namespace api {

class ApiFactory {
public:
    explicit ApiFactory(config::ConfigManager& config_manager);
    ~ApiFactory() = default;

    ApiFactory(const ApiFactory&) = delete;
    ApiFactory& operator=(const ApiFactory&) = delete;

    ApiClientPtr createClient(const std::string& provider);

    std::vector<std::string> getAvailableProviders() const;

    bool isProviderSupported(const std::string& provider) const;

    void registerProvider(const std::string& provider,
                         std::function<ApiClientPtr(const config::ApiConfig&)> creator);

    std::map<std::string, std::string> getProviderInfo() const;

private:
    config::ConfigManager& config_manager_;
    std::map<std::string, std::function<ApiClientPtr(const config::ApiConfig&)>> creators_;

    void initializeBuiltinProviders();

    ApiClientPtr createAnthropicClient(const config::ApiConfig& config);
    ApiClientPtr createOpenAIClient(const config::ApiConfig& config);
    ApiClientPtr createGeminiClient(const config::ApiConfig& config);
    ApiClientPtr createCohereClient(const config::ApiConfig& config);
};

} // namespace api