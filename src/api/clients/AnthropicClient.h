#pragma once

#include "../base/IApiClient.h"
#include "../base/HttpClient.h"
#include "../../config/ApiConfig.h"
#include <memory>

namespace api {

class AnthropicClient : public IApiClient {
public:
    explicit AnthropicClient(const config::ApiConfig& config);
    ~AnthropicClient() override = default;

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
    std::string buildMessagePayload(const MessageRequest& request) const;
    ApiResponse parseResponse(const HttpResponse& http_response) const;
};

} // namespace api