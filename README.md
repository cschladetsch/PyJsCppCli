# AI CLI - Multi-API C++ Connection Framework

![CLI Demo 1](Resources/Demo.gif)
![CLI Demo 2](Resources/Demo2.gif)
![CLI Demo 3](Demo3.gif)

A comprehensive C++ application framework for connecting to multiple AI APIs with a unified interface. This project provides a robust, factory-pattern-based solution for managing connections to various AI service providers including Anthropic Claude, OpenAI, Google Gemini, and Cohere.

**Version:** 0.3.0 | **C++ Standard:** C++23 | **License:** MIT

## Overview

This application demonstrates modern C++ design patterns for API integration, featuring:

- **Multi-API Support**: Unified interface for Anthropic Claude, OpenAI, Google Gemini, and Cohere APIs
- **Factory Pattern Implementation**: Clean, extensible design for creating API clients
- **Configuration-Driven**: JSON-based configuration system with local overrides
- **Connection Pooling**: Efficient HTTP connection management
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Modern C++**: Leverages C++23 features for clean, efficient code
- **Cross-Platform**: Builds on Windows, Linux, and macOS

## Architecture

The application follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│                Main App                 │
├─────────────────────────────────────────┤
│            API Factory              │
├─────────────────────────────────────────┤
│     Global API Interface (IApiClient)   │
├─────────────────────────────────────────┤
│  AnthropicClient │ OpenAIClient │ etc.  │
├─────────────────────────────────────────┤
│         HTTP Connection Pool            │
├─────────────────────────────────────────┤
│        Configuration Manager            │
└─────────────────────────────────────────┘
```

## Configuration System

### config.json (Template)
The base configuration template defining all supported APIs and their settings:

```json
{
  "apis": {
    "anthropic": {
      "name": "Anthropic Claude API",
      "base_url": "https://api.anthropic.com",
      "version": "v1",
      "endpoints": {
        "messages": "/v1/messages",
        "models": "/v1/models"
      },
      "auth": {
        "type": "header",
        "header_name": "x-api-key",
        "env_var": "ANTHROPIC_API_KEY"
      },
      "default_model": "claude-3-sonnet-20240229",
      "max_tokens": 4096,
      "timeout": 30000
    }
  }
}
```

### config.local (Runtime Configuration)
A copy of `config.json` that the application reads at runtime. This allows for:
- Local customization without affecting the template
- Environment-specific settings
- API key management through environment variables
- Testing with different configurations

**Setup**: Copy `config.json` to `config.local` and customize as needed:
```bash
cp config.json config.local
```

## API Support

### Supported APIs

| Provider | Status | Authentication | Models |
|----------|--------|----------------|---------|
| **Anthropic Claude** | ✅ | API Key (Header) | claude-3-sonnet, claude-3-opus |
| **OpenAI** | ✅ | Bearer Token | gpt-4, gpt-3.5-turbo |
| **Google Gemini** | ✅ | API Key (Query) | gemini-pro |
| **Cohere** | ✅ | Bearer Token | command, command-r |

### Authentication Methods

The framework supports multiple authentication patterns:

1. **Header-based**: API key in custom header (Anthropic)
2. **Bearer Token**: OAuth-style bearer authentication (OpenAI, Cohere)
3. **Query Parameter**: API key as URL parameter (Gemini)

All API keys are loaded from environment variables for security.

## Installation & Setup

### Prerequisites

- **C++23 compatible compiler** (GCC 13+, Clang 15+, MSVC 2022)
- **CMake** 3.10 or higher
- **Development libraries**:
  - libcurl (for HTTP requests)
  - nlohmann/json (for JSON parsing)
  - OpenSSL (for HTTPS)

#### Linux/Ubuntu
```bash
sudo apt update
sudo apt install build-essential cmake libcurl4-openssl-dev libssl-dev nlohmann-json3-dev
```

#### macOS
```bash
brew install cmake curl openssl nlohmann-json
```

#### Windows
```bash
# Using vcpkg
vcpkg install curl openssl nlohmann-json
```

### Build Instructions

1. **Clone and configure**:
```bash
git clone <repository-url>
cd PyClaudeCli
cp config.json config.local
```

2. **Set up API keys**:
```bash
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export COHERE_API_KEY="your-cohere-key"
```

3. **Build the project**:
```bash
# Quick build
./b

# Or manual CMake build
mkdir build && cd build
cmake .. -DCMAKE_CXX_COMPILER=clang++
make -j$(nproc)
```

4. **Run tests**:
```bash
./t                 # All tests
./t --cpp          # C++ API tests only
./t --unit         # Unit tests
./t --integration  # Integration tests
```

## Usage Examples

### Basic API Connection

```cpp
#include "api_factory.h"
#include "config_manager.h"

int main() {
    // Load configuration
    ConfigManager config("./config.local");

    // Create API factory
    ApiFactory factory(config);

    // Get Anthropic client
    auto claude_client = factory.createClient("anthropic");
    if (claude_client) {
        auto response = claude_client->sendMessage("Hello, Claude!");
        std::cout << response << std::endl;
    }

    // Get OpenAI client
    auto openai_client = factory.createClient("openai");
    if (openai_client) {
        auto response = openai_client->sendMessage("Hello, GPT!");
        std::cout << response << std::endl;
    }

    return 0;
}
```

### Advanced Configuration

```cpp
// Custom configuration overrides
ConfigManager config("./config.local");
config.setApiTimeout("anthropic", 60000);  // 60 second timeout
config.setMaxTokens("openai", 8192);       // Increase token limit

// Use specific models
auto claude_client = factory.createClient("anthropic");
claude_client->setModel("claude-3-opus-20240229");

auto gpt_client = factory.createClient("openai");
gpt_client->setModel("gpt-4-turbo");
```

### Error Handling

```cpp
try {
    auto client = factory.createClient("anthropic");
    auto response = client->sendMessage("Test message");
    std::cout << "Response: " << response << std::endl;
} catch (const ApiException& e) {
    std::cerr << "API Error: " << e.what() << std::endl;
} catch (const ConfigException& e) {
    std::cerr << "Config Error: " << e.what() << std::endl;
} catch (const std::exception& e) {
    std::cerr << "General Error: " << e.what() << std::endl;
}
```

## Project Structure

```
src/
├── api/
│   ├── base/
│   │   ├── IApiClient.h          # Global API interface
│   │   ├── ApiException.h        # Exception handling
│   │   └── HttpClient.h          # HTTP client wrapper
│   ├── clients/
│   │   ├── AnthropicClient.h     # Anthropic Claude implementation
│   │   ├── AnthropicClient.cpp
│   │   ├── OpenAIClient.h        # OpenAI implementation
│   │   ├── OpenAIClient.cpp
│   │   ├── GeminiClient.h        # Google Gemini implementation
│   │   ├── GeminiClient.cpp
│   │   ├── CohereClient.h        # Cohere implementation
│   │   └── CohereClient.cpp
│   └── factory/
│       ├── ApiFactory.h          # Factory pattern implementation
│       └── ApiFactory.cpp
├── config/
│   ├── ConfigManager.h           # Configuration management
│   ├── ConfigManager.cpp
│   └── ApiConfig.h               # Configuration structures
├── utils/
│   ├── ConnectionPool.h          # HTTP connection pooling
│   ├── ConnectionPool.cpp
│   ├── Logger.h                  # Logging utilities
│   └── Logger.cpp
└── main.cpp                      # Application entry point

config.json                       # Configuration template
config.local                      # Runtime configuration (copy of config.json)
CMakeLists.txt                    # Build configuration
README.md                         # This file
```

## Design Patterns

### 1. Factory Pattern
The `ApiFactory` class implements the factory pattern to create appropriate API client instances:

```cpp
class ApiFactory {
public:
    std::unique_ptr<IApiClient> createClient(const std::string& provider);

private:
    ConfigManager& config_;
    std::map<std::string, std::function<std::unique_ptr<IApiClient>()>> creators_;
};
```

### 2. Strategy Pattern
Each API client implements the `IApiClient` interface, allowing interchangeable use:

```cpp
class IApiClient {
public:
    virtual ~IApiClient() = default;
    virtual std::string sendMessage(const std::string& message) = 0;
    virtual void setModel(const std::string& model) = 0;
    virtual std::vector<std::string> getAvailableModels() = 0;
};
```

### 3. Singleton Pattern
The `ConfigManager` ensures single instance for configuration access:

```cpp
class ConfigManager {
public:
    static ConfigManager& getInstance();
    ApiConfig getApiConfig(const std::string& provider);

private:
    ConfigManager() = default;
    static std::unique_ptr<ConfigManager> instance_;
};
```

## Testing

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: API interaction testing
3. **Configuration Tests**: Config loading and validation
4. **Factory Tests**: Factory pattern verification

### Running Tests

```bash
# All tests
./t

# Specific test categories
./t --unit
./t --integration
./t --cpp

# With coverage
./t --coverage

# Quick smoke test
./t --quick
```

### Test Configuration

Tests use mock configurations and can run without real API keys:

```json
{
  "test_mode": true,
  "mock_responses": true,
  "apis": {
    "mock_anthropic": {
      "base_url": "http://localhost:8080/mock"
    }
  }
}
```

## Security Considerations

### API Key Management
- **Environment Variables**: All API keys loaded from environment
- **No Hardcoding**: Keys never stored in source code or config files
- **Secure Transmission**: HTTPS only for all API communications

### Input Validation
- **Sanitization**: All user inputs sanitized before API calls
- **Size Limits**: Message and response size limits enforced
- **Rate Limiting**: Built-in rate limiting to prevent abuse

### Error Handling
- **No Information Leakage**: Error messages don't expose sensitive data
- **Graceful Degradation**: Fallback behavior for API failures
- **Audit Logging**: Optional logging for security monitoring

## Performance Optimization

### Connection Pooling
- **Persistent Connections**: Reuse HTTP connections for efficiency
- **Connection Limits**: Configurable connection pool sizes
- **Timeout Management**: Proper timeout handling for reliability

### Caching
- **Response Caching**: Optional caching for repeated requests
- **Model Metadata**: Cache model information to reduce API calls
- **Configuration Caching**: In-memory config caching for performance

### Memory Management
- **RAII**: Resource Acquisition Is Initialization pattern
- **Smart Pointers**: Automatic memory management
- **Move Semantics**: Efficient object transfer

## Monitoring and Logging

### Log Levels
- **ERROR**: Critical errors and exceptions
- **WARN**: Warning conditions and fallbacks
- **INFO**: General operational information
- **DEBUG**: Detailed debugging information

### Metrics
- **Request Count**: Track API usage per provider
- **Response Times**: Monitor API performance
- **Error Rates**: Track failure rates per API
- **Connection Pool**: Monitor connection utilization

## Troubleshooting

### Common Issues

#### 1. Configuration Loading Failed
```
Error: Failed to load config.local
Solution: Ensure config.local exists and is valid JSON
```

#### 2. API Authentication Failed
```
Error: 401 Unauthorized
Solution: Check API key environment variables
```

#### 3. Network Connection Issues
```
Error: Connection timeout
Solution: Check internet connectivity and API endpoints
```

#### 4. Build Errors
```
Error: Could not find nlohmann/json
Solution: Install development dependencies
```

### Debug Mode

Enable debug logging for detailed troubleshooting:

```cpp
Logger::setLevel(LogLevel::DEBUG);
```

Or through configuration:
```json
{
  "logging": {
    "level": "DEBUG",
    "log_requests": true,
    "log_responses": true
  }
}
```

## Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Install pre-commit hooks**: `./setup-hooks.sh`
4. **Make changes** and ensure tests pass
5. **Submit pull request**

### Code Standards

- **C++23 Standard**: Use modern C++ features
- **Google Style**: Follow Google C++ style guide
- **Documentation**: Doxygen comments for all public APIs
- **Testing**: Unit tests for all new functionality

### Release Process

1. **Version Bump**: Update version in CMakeLists.txt
2. **Changelog**: Update CHANGELOG.md with changes
3. **Testing**: Run full test suite
4. **Tagging**: Create git tag for release
5. **Documentation**: Update documentation as needed

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **nlohmann/json**: Excellent JSON library for C++
- **libcurl**: Reliable HTTP client library
- **CMake**: Modern build system
- **AI API Providers**: Anthropic, OpenAI, Google, Cohere for their excellent APIs

---

For more detailed information, see the individual component documentation in the `docs/` directory.