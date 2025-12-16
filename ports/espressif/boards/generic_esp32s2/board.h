/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2025
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
 */

#ifndef GENERIC_ESP32S2_H_
#define GENERIC_ESP32S2_H_

//--------------------------------------------------------------------+
// Boot Controls
//--------------------------------------------------------------------+

// Use the BOOT/IO0 button for manual UF2 entry when present.
#define PIN_BUTTON_UF2        0

//--------------------------------------------------------------------+
// USB UF2 Identity
//--------------------------------------------------------------------+

#define USB_VID                  0x303A
#define USB_PID                  0x700A
#define USB_MANUFACTURER         "Generic"
#define USB_PRODUCT              "ESP32-S2 Bootloader"

#define UF2_PRODUCT_NAME         USB_MANUFACTURER " " USB_PRODUCT
#define UF2_BOARD_ID             "ESP32S2-Generic-0"
#define UF2_VOLUME_LABEL         "ESP32S2BOOT"
#define UF2_INDEX_URL            "https://github.com/adafruit/tinyuf2"

#endif
