#pragma once

#include <string>
#include <vector>
#include <memory>
#include <map>

namespace api {

struct ApiResponse {
    std::string content;
    int status_code;
    std::map<std::string, std::string> headers;
    bool success;
    std::string error_message;
};

struct MessageRequest {
    std::string message;
    std::string model;
    int max_tokens;
    double temperature;
    std::vector<std::string> stop_sequences;
};

class IApiClient {
public:
    virtual ~IApiClient() = default;

    virtual ApiResponse sendMessage(const MessageRequest& request) = 0;

    virtual std::vector<std::string> getAvailableModels() = 0;

    virtual void setModel(const std::string& model) = 0;

    virtual std::string getCurrentModel() const = 0;

    virtual void setMaxTokens(int max_tokens) = 0;

    virtual void setTemperature(double temperature) = 0;

    virtual bool isConnected() const = 0;

    virtual std::string getProviderName() const = 0;

    virtual void testConnection() = 0;

    virtual std::map<std::string, std::string> getConnectionInfo() const = 0;
};

using ApiClientPtr = std::unique_ptr<IApiClient>;

} // namespace api