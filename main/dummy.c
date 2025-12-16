// Minimal component used to satisfy PlatformIO's ESP-IDF build pipeline when
// the real TinyUF2 build is skipped.
#include <stdint.h>

uint32_t tinyuf2_placeholder_component(void) {
    return 0xCAFECAFEu;
}
