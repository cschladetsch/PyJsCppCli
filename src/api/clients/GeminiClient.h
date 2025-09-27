#pragma once

#include "../base/IApiClient.h"
#include "../base/HttpClient.h"
#include "../../config/ApiConfig.h"
#include <memory>

namespace api {

class GeminiClient : public IApiClient {
public:
    explicit GeminiClient(const config::ApiConfig& config);
    ~GeminiClient() override = default;

    ApiResponse sendMessage(const MessageRequest& request) override;
    std::vector<std::string> getAvailableModels() override;
    void setModel(const std::string& model) override;
    std::string getCurrentModel() const override;
    void setMaxTokens(int max_tokens) override;
    void setTemperature(double temperature) override;
    bool isConnected() const override;
    std::string getProviderName() const override;
    void testConnection() override;
    std::map<std::string, std::string> getConnectionInfo() const override;

private:
    config::ApiConfig config_;
    std::unique_ptr<HttpClient> http_client_;
    std::string current_model_;
    int max_tokens_;
    double temperature_;
    bool connected_;

    std::string buildEndpointUrl(const std::string& endpoint) const;
    std::map<std::string, std::string> buildHeaders() const;
    std::string buildGeneratePayload(const MessageRequest& request) const;
    ApiResponse parseResponse(const HttpResponse& http_response) const;
    std::string addApiKeyToUrl(const std::string& url) const;
};

} // namespace api