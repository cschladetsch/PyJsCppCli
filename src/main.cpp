#include "api/factory/ApiFactory.h"
#include "config/ConfigManager.h"
#include "api/base/ApiException.h"
#include <iostream>
#include <memory>

void demonstrateApiConnections(api::ApiFactory& factory) {
    std::cout << "=== AI CLI - Multi-API Connection Demo ===\n\n";

    auto providers = factory.getAvailableProviders();
    std::cout << "Available providers: ";
    for (size_t i = 0; i < providers.size(); ++i) {
        std::cout << providers[i];
        if (i < providers.size() - 1) std::cout << ", ";
    }
    std::cout << "\n\n";

    // Test each provider
    for (const auto& provider : providers) {
        std::cout << "Testing " << provider << "...\n";

        try {
            auto client = factory.createClient(provider);

            if (client) {
                auto info = client->getConnectionInfo();
                std::cout << "  Provider: " << info["provider"] << "\n";
                std::cout << "  Base URL: " << info["base_url"] << "\n";
                std::cout << "  Model: " << info["model"] << "\n";
                std::cout << "  Connected: " << info["connected"] << "\n";
                std::cout << "  Max Tokens: " << info["max_tokens"] << "\n";
                std::cout << "  Temperature: " << info["temperature"] << "\n";

                // Test a simple message
                api::MessageRequest request;
                request.message = "Hello! Please respond with just 'Hi there!'";
                request.max_tokens = 50;
                request.temperature = 0.7;

                auto response = client->sendMessage(request);
                if (response.success) {
                    std::cout << "  Response: " << response.content << "\n";
                } else {
                    std::cout << "  Error: " << response.error_message << "\n";
                }

                // List available models
                auto models = client->getAvailableModels();
                std::cout << "  Available models: ";
                for (size_t i = 0; i < models.size() && i < 3; ++i) {
                    std::cout << models[i];
                    if (i < std::min(models.size(), static_cast<size_t>(3)) - 1) std::cout << ", ";
                }
                if (models.size() > 3) std::cout << "... (+" << (models.size() - 3) << " more)";
                std::cout << "\n";
            }
        } catch (const api::AuthenticationException& e) {
            std::cout << "  Authentication Error: " << e.what() << "\n";
            std::cout << "  (Check your API key environment variable)\n";
        } catch (const api::ConnectionException& e) {
            std::cout << "  Connection Error: " << e.what() << "\n";
        } catch (const api::ConfigException& e) {
            std::cout << "  Configuration Error: " << e.what() << "\n";
        } catch (const std::exception& e) {
            std::cout << "  Error: " << e.what() << "\n";
        }

        std::cout << "\n";
    }
}

void printUsage(const char* program_name) {
    std::cout << "Usage: " << program_name << " [options]\n\n";
    std::cout << "Options:\n";
    std::cout << "  --config <file>    Use custom config file (default: ./config.local)\n";
    std::cout << "  --test             Test all API connections\n";
    std::cout << "  --list-providers   List available providers\n";
    std::cout << "  --provider <name>  Test specific provider only\n";
    std::cout << "  --help             Show this help message\n\n";
    std::cout << "Examples:\n";
    std::cout << "  " << program_name << " --test\n";
    std::cout << "  " << program_name << " --provider anthropic\n";
    std::cout << "  " << program_name << " --config ./my-config.json --test\n";
}

int main(int argc, char* argv[]) {
    std::string config_file = "./config.local";
    bool test_mode = false;
    bool list_providers = false;
    std::string specific_provider;

    // Parse command line arguments
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];

        if (arg == "--help" || arg == "-h") {
            printUsage(argv[0]);
            return 0;
        } else if (arg == "--config" && i + 1 < argc) {
            config_file = argv[++i];
        } else if (arg == "--test") {
            test_mode = true;
        } else if (arg == "--list-providers") {
            list_providers = true;
        } else if (arg == "--provider" && i + 1 < argc) {
            specific_provider = argv[++i];
            test_mode = true;
        } else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            printUsage(argv[0]);
            return 1;
        }
    }

    try {
        // Initialize configuration
        std::cout << "Loading configuration from: " << config_file << "\n";
        config::ConfigManager config_manager(config_file);

        // Initialize factory
        api::ApiFactory factory(config_manager);

        if (list_providers) {
            auto providers = factory.getAvailableProviders();
            std::cout << "Available providers:\n";
            for (const auto& provider : providers) {
                std::cout << "  - " << provider << "\n";
            }
            return 0;
        }

        if (test_mode) {
            if (!specific_provider.empty()) {
                if (!factory.isProviderSupported(specific_provider)) {
                    std::cerr << "Provider '" << specific_provider << "' is not supported or configured.\n";
                    return 1;
                }

                std::cout << "Testing provider: " << specific_provider << "\n\n";
                auto client = factory.createClient(specific_provider);

                auto info = client->getConnectionInfo();
                for (const auto& pair : info) {
                    std::cout << "  " << pair.first << ": " << pair.second << "\n";
                }

                api::MessageRequest request;
                request.message = "Hello! Please respond with a brief greeting.";
                request.max_tokens = 100;

                auto response = client->sendMessage(request);
                if (response.success) {
                    std::cout << "\nResponse: " << response.content << "\n";
                } else {
                    std::cout << "\nError: " << response.error_message << "\n";
                }
            } else {
                demonstrateApiConnections(factory);
            }
        } else {
            std::cout << "AI CLI Framework initialized successfully!\n";
            std::cout << "Use --help for usage information.\n";
        }

    } catch (const api::ConfigException& e) {
        std::cerr << "Configuration Error: " << e.what() << std::endl;
        std::cerr << "\nPlease ensure:\n";
        std::cerr << "1. config.local exists (copy from config.json)\n";
        std::cerr << "2. Required environment variables are set:\n";
        std::cerr << "   - ANTHROPIC_API_KEY\n";
        std::cerr << "   - OPENAI_API_KEY\n";
        std::cerr << "   - GEMINI_API_KEY\n";
        std::cerr << "   - COHERE_API_KEY\n";
        return 1;
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}