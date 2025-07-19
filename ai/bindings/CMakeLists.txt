cmake_minimum_required(VERSION 3.10)
project(VariableAPI)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add executable
add_executable(variable_api_test variable_api.cpp)

# Add library for use in other projects
add_library(variable_api STATIC variable_api.cpp)

# Set compiler flags
target_compile_options(variable_api_test PRIVATE -Wall -Wextra)
target_compile_options(variable_api PRIVATE -Wall -Wextra)

# Find Doxygen
find_package(Doxygen)

if(DOXYGEN_FOUND)
    # Set input and output files
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/../../Doxyfile)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)

    # Request to configure the file
    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
    message("Doxygen build started")

    # Note the option ALL which allows to build the docs together with the application
    add_custom_target(doc_doxygen ALL
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../..
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM)

    # Create Doxygen directory if it doesn't exist
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../Doxygen)
else (DOXYGEN_FOUND)
    message("Doxygen need to be installed to generate the doxygen documentation")
endif (DOXYGEN_FOUND)

# Install targets
install(TARGETS variable_api_test DESTINATION bin)
install(TARGETS variable_api DESTINATION lib)
install(FILES variable_api.cpp DESTINATION include)