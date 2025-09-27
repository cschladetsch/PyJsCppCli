#pragma once

#include <stdexcept>
#include <string>

namespace api {

class ApiException : public std::runtime_error {
public:
    explicit ApiException(const std::string& message)
        : std::runtime_error(message), error_code_(0) {}

    ApiException(const std::string& message, int code)
        : std::runtime_error(message), error_code_(code) {}

    int getErrorCode() const noexcept { return error_code_; }

private:
    int error_code_;
};

class ConfigException : public std::runtime_error {
public:
    explicit ConfigException(const std::string& message)
        : std::runtime_error(message) {}
};

class ConnectionException : public ApiException {
public:
    explicit ConnectionException(const std::string& message)
        : ApiException(message) {}

    ConnectionException(const std::string& message, int code)
        : ApiException(message, code) {}
};

class AuthenticationException : public ApiException {
public:
    explicit AuthenticationException(const std::string& message)
        : ApiException(message, 401) {}
};

class RateLimitException : public ApiException {
public:
    explicit RateLimitException(const std::string& message)
        : ApiException(message, 429) {}
};

class InvalidRequestException : public ApiException {
public:
    explicit InvalidRequestException(const std::string& message)
        : ApiException(message, 400) {}
};

} // namespace api