#pragma once

#include <string>
#include <map>
#include <vector>

namespace config {

struct AuthConfig {
    std::string type;           // "header", "bearer", "query_param"
    std::string header_name;    // For header type
    std::string param_name;     // For query_param type
    std::string env_var;        // Environment variable name
    std::string token;          // Actual token value (loaded from env_var)
};

struct EndpointConfig {
    std::map<std::string, std::string> endpoints;
};

struct ConnectionPoolConfig {
    int max_connections = 10;
    bool keep_alive = true;
    bool verify_ssl = true;
    int retry_attempts = 3;
    int retry_delay = 1000; // milliseconds
};

struct LoggingConfig {
    std::string level = "INFO";
    bool log_requests = false;
    bool log_responses = false;
};

struct ApiConfig {
    std::string name;
    std::string base_url;
    std::string version;
    EndpointConfig endpoints;
    AuthConfig auth;
    std::string default_model;
    int max_tokens = 4096;
    int timeout = 30000; // milliseconds
    double temperature = 0.7;
    std::vector<std::string> stop_sequences;
};

struct GlobalConfig {
    std::map<std::string, ApiConfig> apis;
    ConnectionPoolConfig connection_pool;
    LoggingConfig logging;
};

} // namespace config