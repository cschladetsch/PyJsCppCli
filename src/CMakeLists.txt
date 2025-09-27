cmake_minimum_required(VERSION 3.10)
project(AI_CLI_Framework)

# Set C++ standard
set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(PkgConfig REQUIRED)
find_package(CURL REQUIRED)

# Find nlohmann/json
find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
    # Fallback: try to find it via pkg-config
    pkg_check_modules(NLOHMANN_JSON REQUIRED nlohmann_json)
endif()

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR})
include_directories(${CURL_INCLUDE_DIRS})

# Source files
set(SOURCES
    main.cpp
    api/base/HttpClient.cpp
    api/factory/ApiFactory.cpp
    api/clients/AnthropicClient.cpp
    api/clients/OpenAIClient.cpp
    api/clients/GeminiClient.cpp
    api/clients/CohereClient.cpp
    config/ConfigManager.cpp
)

# Header files
set(HEADERS
    api/base/IApiClient.h
    api/base/ApiException.h
    api/base/HttpClient.h
    api/factory/ApiFactory.h
    api/clients/AnthropicClient.h
    api/clients/OpenAIClient.h
    api/clients/GeminiClient.h
    api/clients/CohereClient.h
    config/ApiConfig.h
    config/ConfigManager.h
)

# Create executable
add_executable(ai_cli_framework ${SOURCES} ${HEADERS})

# Link libraries
target_link_libraries(ai_cli_framework ${CURL_LIBRARIES})

# Link nlohmann/json
if(nlohmann_json_FOUND)
    target_link_libraries(ai_cli_framework nlohmann_json::nlohmann_json)
else()
    target_include_directories(ai_cli_framework PRIVATE ${NLOHMANN_JSON_INCLUDE_DIRS})
    target_link_libraries(ai_cli_framework ${NLOHMANN_JSON_LIBRARIES})
endif()

# Compiler flags
target_compile_options(ai_cli_framework PRIVATE
    -Wall
    -Wextra
    -Wpedantic
    -Werror
    $<$<CONFIG:Debug>:-g -O0>
    $<$<CONFIG:Release>:-O3 -DNDEBUG>
)

# Set output directory
set_target_properties(ai_cli_framework PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/Bin
)

# Install target
install(TARGETS ai_cli_framework
    RUNTIME DESTINATION bin
)

# Print configuration info
message(STATUS "AI CLI Framework Configuration:")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "  CURL Found: ${CURL_FOUND}")
message(STATUS "  CURL Version: ${CURL_VERSION_STRING}")
if(nlohmann_json_FOUND)
    message(STATUS "  nlohmann/json: Found via CMake")
else()
    message(STATUS "  nlohmann/json: Found via pkg-config")
endif()
message(STATUS "  Output Directory: ${CMAKE_SOURCE_DIR}/Bin")

# Optional: Create a build info header
configure_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/build_config.h.in
    ${CMAKE_CURRENT_BINARY_DIR}/build_config.h
    @ONLY
)