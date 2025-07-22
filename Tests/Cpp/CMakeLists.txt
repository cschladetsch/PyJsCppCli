cmake_minimum_required(VERSION 3.10)
project(VariableAPITests)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add test executable
add_executable(TestVariableApi test_VariableApi.cpp)

# Set compiler flags
target_compile_options(TestVariableApi PRIVATE -Wall -Wextra)

# Link filesystem library if needed
target_link_libraries(TestVariableApi stdc++fs)

# Add custom test target
add_custom_target(run_cpp_tests
    COMMAND TestVariableApi
    DEPENDS TestVariableApi
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMENT "Running C++ Variable API tests"
)