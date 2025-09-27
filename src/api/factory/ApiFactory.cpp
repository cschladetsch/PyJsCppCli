#include "ApiFactory.h"
#include "../clients/AnthropicClient.h"
#include "../clients/OpenAIClient.h"
#include "../clients/GeminiClient.h"
#include "../clients/CohereClient.h"
#include "../base/ApiException.h"

namespace api {

ApiFactory::ApiFactory(config::ConfigManager& config_manager)
    : config_manager_(config_manager) {
    initializeBuiltinProviders();
}

ApiClientPtr ApiFactory::createClient(const std::string& provider) {
    auto it = creators_.find(provider);
    if (it == creators_.end()) {
        throw ApiException("Unsupported provider: " + provider);
    }

    if (!config_manager_.hasProvider(provider)) {
        throw ConfigException("Provider '" + provider + "' not found in configuration");
    }

    try {
        auto config = config_manager_.getApiConfig(provider);
        return it->second(config);
    } catch (const std::exception& e) {
        throw ApiException("Failed to create client for provider '" + provider + "': " + e.what());
    }
}

std::vector<std::string> ApiFactory::getAvailableProviders() const {
    std::vector<std::string> providers;
    for (const auto& pair : creators_) {
        if (config_manager_.hasProvider(pair.first)) {
            providers.push_back(pair.first);
        }
    }
    return providers;
}

bool ApiFactory::isProviderSupported(const std::string& provider) const {
    return creators_.find(provider) != creators_.end() &&
           config_manager_.hasProvider(provider);
}

void ApiFactory::registerProvider(const std::string& provider,
                                std::function<ApiClientPtr(const config::ApiConfig&)> creator) {
    creators_[provider] = creator;
}

std::map<std::string, std::string> ApiFactory::getProviderInfo() const {
    std::map<std::string, std::string> info;

    for (const auto& provider : getAvailableProviders()) {
        try {
            auto config = config_manager_.getApiConfig(provider);
            info[provider] = config.name + " (" + config.base_url + ")";
        } catch (const std::exception& e) {
            info[provider] = "Error: " + std::string(e.what());
        }
    }

    return info;
}

void ApiFactory::initializeBuiltinProviders() {
    creators_["anthropic"] = [this](const config::ApiConfig& config) {
        return createAnthropicClient(config);
    };

    creators_["openai"] = [this](const config::ApiConfig& config) {
        return createOpenAIClient(config);
    };

    creators_["gemini"] = [this](const config::ApiConfig& config) {
        return createGeminiClient(config);
    };

    creators_["cohere"] = [this](const config::ApiConfig& config) {
        return createCohereClient(config);
    };
}

ApiClientPtr ApiFactory::createAnthropicClient(const config::ApiConfig& config) {
    return std::make_unique<AnthropicClient>(config);
}

ApiClientPtr ApiFactory::createOpenAIClient(const config::ApiConfig& config) {
    return std::make_unique<OpenAIClient>(config);
}

ApiClientPtr ApiFactory::createGeminiClient(const config::ApiConfig& config) {
    return std::make_unique<GeminiClient>(config);
}

ApiClientPtr ApiFactory::createCohereClient(const config::ApiConfig& config) {
    return std::make_unique<CohereClient>(config);
}

} // namespace api