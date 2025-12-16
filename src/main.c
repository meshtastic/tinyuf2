/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Ha Thach (tinyusb.org)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 *
 */

#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>

#include "board_api.h"
#include "uf2.h"
#include "tusb.h"

//--------------------------------------------------------------------+
// MACRO CONSTANT TYPEDEF PROTOTYPES
//--------------------------------------------------------------------+
static volatile uint32_t _timer_count = 0;

//--------------------------------------------------------------------+
//
//--------------------------------------------------------------------+
static bool check_dfu_mode(void);

int main(void) {
  board_init();
  if (board_init2) board_init2();
  TUF2_LOG1("TinyUF2\r\n");

#if TINYUF2_PROTECT_BOOTLOADER
  board_flash_protect_bootloader(true);
#endif

  // if not DFU mode, jump to App
  if (!check_dfu_mode()) {
    TUF2_LOG1("Jump to application\r\n");
    if (board_teardown) board_teardown();
    if (board_teardown2) board_teardown2();
    board_app_jump();
    TUF2_LOG1("Failed to jump\r\n");
    while (1) {}
  }

  TUF2_LOG1("Start DFU mode\r\n");
  board_dfu_init();
  board_flash_init();
  uf2_init();

  tud_init(BOARD_TUD_RHPORT);

#if CFG_TUSB_OS == OPT_OS_NONE || CFG_TUSB_OS == OPT_OS_PICO
  while(1) {
    tud_task();
  }
#endif
}

// return true if start DFU mode, else App mode
static bool check_dfu_mode(void) {
  // Check if app is valid
  if (!board_app_valid()) {
    TUF2_LOG1("App invalid\r\n");
    return true;
  }
  if (board_app_valid2 && !board_app_valid2()) {
    TUF2_LOG1("App invalid\r\n");
    return true;
  }

#if TINYUF2_DBL_TAP_DFU
   TUF2_LOG1_HEX(TINYUF2_DBL_TAP_REG);

  switch(TINYUF2_DBL_TAP_REG) {
    case DBL_TAP_MAGIC_QUICK_BOOT:
      // Boot to app quickly
      TUF2_LOG1("Quick boot to App\r\n");
      TINYUF2_DBL_TAP_REG = 0;
      return false;

    case DBL_TAP_MAGIC:
      // Double tap occurred
      TUF2_LOG1("Double Tap Reset\r\n");
      TINYUF2_DBL_TAP_REG = 0;
      return true;

    case DBL_TAP_MAGIC_ERASE_APP:
      TUF2_LOG1("Erase app\r\n");
      TINYUF2_DBL_TAP_REG = 0;
      board_flash_erase_app();
      return true;

    default:
      break;
  }

  // Register our first reset for double reset detection
  TINYUF2_DBL_TAP_REG = DBL_TAP_MAGIC;

  _timer_count = 0;
  board_timer_start(1);

  // neopixel may need a bit of prior delay to work
  // while(_timer_count < 1) {}

  // delay a fraction of second if Reset pin is tap during this delay --> we will enter dfu
  while(_timer_count < TINYUF2_DBL_TAP_DELAY) {}
  board_timer_stop();

  TINYUF2_DBL_TAP_REG = 0;
#endif

  return false;
}

//--------------------------------------------------------------------+
// Device callbacks
//--------------------------------------------------------------------+

// Invoked when device is plugged and configured
void tud_mount_cb(void) {
}

// Invoked when device is unplugged
void tud_umount_cb(void) {
}

void board_timer_handler(void) {
  _timer_count++;
}

//--------------------------------------------------------------------+
// Logger newlib retarget
//--------------------------------------------------------------------+

// Enable only with LOG is enabled (Note: ESP32-S2 has built-in support already)
#if (CFG_TUSB_DEBUG || TUF2_LOG) && (CFG_TUSB_MCU != OPT_MCU_ESP32S2 && CFG_TUSB_MCU != OPT_MCU_RP2040)
#if defined(LOGGER_RTT)
#include "SEGGER_RTT.h"
#endif

TU_ATTR_USED int _write (int fhdl, const void *buf, size_t count) {
  (void) fhdl;

#if defined(LOGGER_RTT)
  SEGGER_RTT_Write(0, (char*) buf, (int) count);
  return count;
#else
  return board_uart_write(buf, count);
#endif
}

#endif
