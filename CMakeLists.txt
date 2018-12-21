cmake_minimum_required(VERSION 3.10)
project(conan_build_tool)
execute_process(
	  COMMAND git describe --always --long --dirty=-modified
	  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
	  OUTPUT_VARIABLE GIT_VERSION_FULL
	  OUTPUT_STRIP_TRAILING_WHITESPACE
		)

if (${GIT_VERSION_FULL} MATCHES "^[0-9]+\\.[0-9]+\\.[0-9]+.*$" )
    string(REGEX REPLACE "^([0-9]+\\.[0-9]+\\.[0-9]+)(.*$)" "\\1" GIT_VERSION ${GIT_VERSION_FULL} )
    string(REGEX REPLACE "^([0-9]+\\.[0-9]+\\.[0-9]+)(.*$)" "\\2" GIT_VERSION_SUFFIX ${GIT_VERSION_FULL} )
else()
    set(GIT_VERSION "0.0.2")
    set(GIT_VERSION_SUFFIX ${GIT_VERSION_FULL} )

endif()	

message(${GIT_VERSION})
message(${GIT_VERSION_SUFFIX})


configure_file(setup.py.in setup.py @ONLY)

add_custom_target(sdist ALL python3 ${CMAKE_CURRENT_BINARY_DIR}/setup.py sdist
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} )
                  
add_custom_target(wheel ALL python3 ${CMAKE_CURRENT_BINARY_DIR}/setup.py bdist_wheel
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} )
                  
add_custom_target(upload python3 ${CMAKE_CURRENT_BINARY_DIR}/setup.py sdist upload
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} )
add_custom_target(inst python3 ${CMAKE_CURRENT_BINARY_DIR}/setup.py install
                  WORKING_DIRECTORY ${CMAKE_SOURCE_DIR} )

