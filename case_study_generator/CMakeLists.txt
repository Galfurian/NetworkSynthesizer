#################################################
# Check CMAKE Version.
cmake_minimum_required(VERSION 2.8.4)

#################################################
# Create the project...
project(MilpTestCaseGenerator CXX)

#################################################
# Set the project name...
SET(PROJECT_NAME MilpTestCaseGenerator)
SET(PROJECT_SOURCE_DIR .)

add_compile_options(-ggdb)
add_compile_options(-g3)

#################################################
# Initialize CXXFLAGS...
set(CMAKE_CXX_STANDARD 11)

#################################################
# Add project sources and includes...
set(PROJECT_SRC
        main.cpp
        utils/utils.cpp
        components/problemInstance.cpp
        components/dataFlow.cpp
        components/contiguity.cpp
        components/channel.cpp
        components/node.cpp
        components/zone.cpp
        components/task.cpp
        test_cases/test_case_01.cpp
        test_cases/test_case_02.cpp
        test_cases/test_case_03.cpp
        test_cases/stress_test_generator.cpp
        test_cases/corner_case_1.cpp
        )

set(PROJECT_INC
        ${CMAKE_SOURCE_DIR}/components
        ${CMAKE_SOURCE_DIR}/utils
        ${CMAKE_SOURCE_DIR}/test_cases
        )

#################################################
# Add project includes...
include_directories(
        ${PROJECT_INC}
)

#################################################
# Add the executable...
add_executable(
        ${PROJECT_NAME}
        ${PROJECT_SRC}
)

install(TARGETS ${PROJECT_NAME}
        DESTINATION ~/bin)

add_custom_target(install_${PROJECT_NAME}
        $(MAKE) install
        DEPENDS ${PROJECT_NAME}
        COMMENT "Installing ${PROJECT_NAME}")
