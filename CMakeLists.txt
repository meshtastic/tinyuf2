cmake_minimum_required(VERSION 3.17)

if(DEFINED TINYUF2_PLATFORMIO_SKIP AND TINYUF2_PLATFORMIO_SKIP)
  if(NOT DEFINED ENV{IDF_PATH})
    message(FATAL_ERROR "IDF_PATH is not set")
  endif ()

  if(NOT DEFINED BOARD)
    message(FATAL_ERROR "BOARD must be defined when skipping TinyUF2 build")
  endif ()

  if(BOARD MATCHES "esp32s3")
    set(IDF_TARGET "esp32s3" CACHE STRING "" FORCE)
  elseif(BOARD MATCHES "esp32s2")
    set(IDF_TARGET "esp32s2" CACHE STRING "" FORCE)
  endif ()

  include($ENV{IDF_PATH}/tools/cmake/project.cmake)
  project(tinyuf2_platformio_placeholder)
  return()
endif ()

include(ports/family_support.cmake)

# Espressif has its own build system
if(NOT FAMILY STREQUAL espressif)
  project(tinyuf2_all C ASM)
endif ()

add_subdirectory(ports/${FAMILY})
