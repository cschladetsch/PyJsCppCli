#pragma once

#include <string>
#include <map>
#include <memory>
#include <curl/curl.h>

namespace api {

struct HttpRequest {
    std::string url;
    std::string method = "GET";
    std::string body;
    std::map<std::string, std::string> headers;
    int timeout = 30000; // milliseconds
};

struct HttpResponse {
    std::string body;
    int status_code;
    std::map<std::string, std::string> headers;
    bool success;
    std::string error_message;
};

class HttpClient {
public:
    HttpClient();
    ~HttpClient();

    HttpClient(const HttpClient&) = delete;
    HttpClient& operator=(const HttpClient&) = delete;

    HttpResponse send(const HttpRequest& request);

    HttpResponse get(const std::string& url,
                    const std::map<std::string, std::string>& headers = {});

    HttpResponse post(const std::string& url,
                     const std::string& body,
                     const std::map<std::string, std::string>& headers = {});

    HttpResponse put(const std::string& url,
                    const std::string& body,
                    const std::map<std::string, std::string>& headers = {});

    HttpResponse delete_(const std::string& url,
                        const std::map<std::string, std::string>& headers = {});

    void setDefaultTimeout(int timeout_ms);

    void setUserAgent(const std::string& user_agent);

    void setVerifySSL(bool verify);

private:
    CURL* curl_;
    int default_timeout_;
    std::string user_agent_;
    bool verify_ssl_;

    static size_t writeCallback(void* contents, size_t size, size_t nmemb, std::string* response);
    static size_t headerCallback(char* buffer, size_t size, size_t nitems, std::map<std::string, std::string>* headers);

    void setupRequest(CURL* curl, const HttpRequest& request, std::string& response_body,
                     std::map<std::string, std::string>& response_headers);
};

} // namespace api