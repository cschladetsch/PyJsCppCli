cmake_minimum_required(VERSION 3.10)
project(PyClaudeCli)

# Default to Clang if available
if(NOT CMAKE_C_COMPILER)
    find_program(CLANG_C_COMPILER clang)
    if(CLANG_C_COMPILER)
        set(CMAKE_C_COMPILER ${CLANG_C_COMPILER})
    endif()
endif()

if(NOT CMAKE_CXX_COMPILER)
    find_program(CLANG_CXX_COMPILER clang++)
    if(CLANG_CXX_COMPILER)
        set(CMAKE_CXX_COMPILER ${CLANG_CXX_COMPILER})
    endif()
endif()

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Doxygen
find_package(Doxygen)

if(DOXYGEN_FOUND)
    # Find dot (graphviz) for diagram generation
    find_program(DOT_EXECUTABLE dot)
    
    # Set input and output files
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)

    # Request to configure the file
    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
    message("Doxygen build started")

    # Create directories
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/Doxygen)
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/Resources)

    # Create documentation target
    add_custom_target(docs
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM)

    # Add target to convert .dot files to PNG in top-level Resources
    if(DOT_EXECUTABLE)
        add_custom_target(diagrams
            COMMAND find ${CMAKE_CURRENT_SOURCE_DIR} -name "*.dot" -type f | while read dotfile\; do echo "Converting $$dotfile to PNG"\; basename_no_ext=$$(basename "$$dotfile" .dot)\; ${DOT_EXECUTABLE} -Tpng "$$dotfile" -o "${CMAKE_CURRENT_SOURCE_DIR}/Resources/$$basename_no_ext.png"\; done
            DEPENDS docs
            WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
            COMMENT "Converting all .dot files to PNG format in top-level Resources folder"
            VERBATIM)
        
        message(STATUS "Graphviz dot found: ${DOT_EXECUTABLE}")
        message(STATUS "Diagram PNGs will be generated in: ${CMAKE_CURRENT_SOURCE_DIR}/Resources")
    else()
        message(WARNING "dot (graphviz) not found. Diagrams will not be converted to PNG.")
    endif()
    
    message(STATUS "Doxygen found: ${DOXYGEN_EXECUTABLE}")
    message(STATUS "Documentation will be generated in: ${CMAKE_CURRENT_SOURCE_DIR}/Doxygen")
else (DOXYGEN_FOUND)
    message(WARNING "Doxygen not found. Install Doxygen to generate documentation.")
    message(STATUS "On Ubuntu/Debian: sudo apt install doxygen graphviz")
    message(STATUS "On macOS: brew install doxygen graphviz")
endif (DOXYGEN_FOUND)

# Add subdirectories
add_subdirectory(ai/bindings)
add_subdirectory(tests/cpp)

# Add custom target for all tests
add_custom_target(test_all
    COMMAND python3 -m pytest tests/unit/test_variables.py -v
    COMMAND python3 -m pytest tests/integration/test_variable_integration.py -v
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Running all Python tests"
    VERBATIM)

# Add dependency to ensure C++ tests are built before running
add_dependencies(test_all test_variable_api)