cmake_minimum_required(VERSION 3.10)
project(VariableAPITests)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add test executable
add_executable(test_variable_api test_variable_api.cpp)

# Set compiler flags
target_compile_options(test_variable_api PRIVATE -Wall -Wextra)

# Link filesystem library if needed
target_link_libraries(test_variable_api stdc++fs)

# Add custom test target
add_custom_target(run_cpp_tests
    COMMAND test_variable_api
    DEPENDS test_variable_api
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running C++ Variable API tests"
)