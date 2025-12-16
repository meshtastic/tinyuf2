if(NOT DEFINED TINYUF2_PLATFORMIO_SKIP OR NOT TINYUF2_PLATFORMIO_SKIP)
  return()
endif()

idf_component_register(SRCS "dummy.c")
