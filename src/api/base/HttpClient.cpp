#include "HttpClient.h"
#include "ApiException.h"
#include <iostream>
#include <sstream>

namespace api {

HttpClient::HttpClient()
    : curl_(nullptr), default_timeout_(30000), user_agent_("AI-CLI/1.0"), verify_ssl_(true) {
    curl_ = curl_easy_init();
    if (!curl_) {
        throw ConnectionException("Failed to initialize CURL");
    }
}

HttpClient::~HttpClient() {
    if (curl_) {
        curl_easy_cleanup(curl_);
    }
}

HttpResponse HttpClient::send(const HttpRequest& request) {
    if (!curl_) {
        throw ConnectionException("CURL not initialized");
    }

    std::string response_body;
    std::map<std::string, std::string> response_headers;
    HttpResponse response;

    setupRequest(curl_, request, response_body, response_headers);

    CURLcode res = curl_easy_perform(curl_);

    if (res != CURLE_OK) {
        response.success = false;
        response.error_message = curl_easy_strerror(res);
        response.status_code = 0;
        return response;
    }

    long response_code;
    curl_easy_getinfo(curl_, CURLINFO_RESPONSE_CODE, &response_code);

    response.body = response_body;
    response.status_code = static_cast<int>(response_code);
    response.headers = response_headers;
    response.success = (response_code >= 200 && response_code < 300);

    if (!response.success) {
        if (response_code == 401) {
            throw AuthenticationException("Authentication failed: " + response_body);
        } else if (response_code == 429) {
            throw RateLimitException("Rate limit exceeded: " + response_body);
        } else if (response_code >= 400 && response_code < 500) {
            throw InvalidRequestException("Client error: " + response_body);
        } else if (response_code >= 500) {
            throw ConnectionException("Server error: " + response_body, response_code);
        }
    }

    return response;
}

HttpResponse HttpClient::get(const std::string& url,
                           const std::map<std::string, std::string>& headers) {
    HttpRequest request;
    request.url = url;
    request.method = "GET";
    request.headers = headers;
    request.timeout = default_timeout_;
    return send(request);
}

HttpResponse HttpClient::post(const std::string& url,
                            const std::string& body,
                            const std::map<std::string, std::string>& headers) {
    HttpRequest request;
    request.url = url;
    request.method = "POST";
    request.body = body;
    request.headers = headers;
    request.timeout = default_timeout_;
    return send(request);
}

HttpResponse HttpClient::put(const std::string& url,
                           const std::string& body,
                           const std::map<std::string, std::string>& headers) {
    HttpRequest request;
    request.url = url;
    request.method = "PUT";
    request.body = body;
    request.headers = headers;
    request.timeout = default_timeout_;
    return send(request);
}

HttpResponse HttpClient::delete_(const std::string& url,
                               const std::map<std::string, std::string>& headers) {
    HttpRequest request;
    request.url = url;
    request.method = "DELETE";
    request.headers = headers;
    request.timeout = default_timeout_;
    return send(request);
}

void HttpClient::setDefaultTimeout(int timeout_ms) {
    default_timeout_ = timeout_ms;
}

void HttpClient::setUserAgent(const std::string& user_agent) {
    user_agent_ = user_agent;
}

void HttpClient::setVerifySSL(bool verify) {
    verify_ssl_ = verify;
}

size_t HttpClient::writeCallback(void* contents, size_t size, size_t nmemb, std::string* response) {
    size_t total_size = size * nmemb;
    response->append(static_cast<char*>(contents), total_size);
    return total_size;
}

size_t HttpClient::headerCallback(char* buffer, size_t size, size_t nitems,
                                std::map<std::string, std::string>* headers) {
    size_t total_size = size * nitems;
    std::string header(buffer, total_size);

    size_t colon_pos = header.find(':');
    if (colon_pos != std::string::npos) {
        std::string name = header.substr(0, colon_pos);
        std::string value = header.substr(colon_pos + 1);

        // Trim whitespace
        name.erase(0, name.find_first_not_of(" \t"));
        name.erase(name.find_last_not_of(" \t\r\n") + 1);
        value.erase(0, value.find_first_not_of(" \t"));
        value.erase(value.find_last_not_of(" \t\r\n") + 1);

        (*headers)[name] = value;
    }

    return total_size;
}

void HttpClient::setupRequest(CURL* curl, const HttpRequest& request, std::string& response_body,
                            std::map<std::string, std::string>& response_headers) {
    // Reset curl handle
    curl_easy_reset(curl);

    // Set URL
    curl_easy_setopt(curl, CURLOPT_URL, request.url.c_str());

    // Set method
    if (request.method == "POST") {
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request.body.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request.body.length());
    } else if (request.method == "PUT") {
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "PUT");
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, request.body.c_str());
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, request.body.length());
    } else if (request.method == "DELETE") {
        curl_easy_setopt(curl, CURLOPT_CUSTOMREQUEST, "DELETE");
    }

    // Set headers
    struct curl_slist* headers_list = nullptr;
    for (const auto& header : request.headers) {
        std::string header_str = header.first + ": " + header.second;
        headers_list = curl_slist_append(headers_list, header_str.c_str());
    }

    // Add default headers
    if (request.headers.find("User-Agent") == request.headers.end()) {
        std::string ua_header = "User-Agent: " + user_agent_;
        headers_list = curl_slist_append(headers_list, ua_header.c_str());
    }

    if (!request.body.empty() && request.headers.find("Content-Type") == request.headers.end()) {
        headers_list = curl_slist_append(headers_list, "Content-Type: application/json");
    }

    if (headers_list) {
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers_list);
    }

    // Set callbacks
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, writeCallback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_body);
    curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, headerCallback);
    curl_easy_setopt(curl, CURLOPT_HEADERDATA, &response_headers);

    // Set options
    curl_easy_setopt(curl, CURLOPT_TIMEOUT_MS, request.timeout > 0 ? request.timeout : default_timeout_);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_MAXREDIRS, 5L);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYPEER, verify_ssl_ ? 1L : 0L);
    curl_easy_setopt(curl, CURLOPT_SSL_VERIFYHOST, verify_ssl_ ? 2L : 0L);

    // Clean up headers list when done
    if (headers_list) {
        curl_slist_free_all(headers_list);
    }
}

} // namespace api