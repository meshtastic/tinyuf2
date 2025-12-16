# TinyUF2 Bootloader

[![Build Status](https://github.com/adafruit/tinyuf2/workflows/Build/badge.svg)](https://github.com/adafruit/tinyuf2/actions)[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://opensource.org/licenses/MIT)

This repo is cross-platform UF2 Bootloader projects for MCUs based on [TinyUSB](https://github.com/hathach/tinyusb)

```
.
├── apps              # Useful applications such as self-update, erase firmware
├── lib               # Sources from 3rd party such as tinyusb, mcu drivers ...
├── ports             # Port/family specific sources
│   ├── espressif
│   │   └── boards/   # Board specific sources
│   │   └── Makefile  # Makefile for this port
│   └── mimxrt10xx
├── src               # Cross-platform bootloader sources files
```

## Features

Supported features are

- Double tap to enter DFU, reboot to DFU and quick reboot from application
- DFU with MassStorage (MSC)
- Self update with uf2 file
- Indicator: LED, RGB, TFT
- Debug log with uart/swd

Not all features are implemented for all MCUs, following is supported MCUs and its feature

| MCU         | MSC  | Double Reset | Self-update | Write Protection | Neopixel | TFT  |
|:------------| :--: | :----------: |:-----------:| :--------------: |:--------:| :--: |
| ESP32 S2/S3 |  ✔   |   Need RC    |      ✔      |                  |    ✔     |  ✔   |
| K32L2       |  ✔   |      ✔       |             |                  |          |      |
| LPC55       |  ✔   |      ✔       |             |                  |    ✔     |      |
| iMXRT       |  ✔   |      ✔       |      ✔      |                  |    ✔     |      |
| STM32F3     |  ✔   |      ✔       |      ✔      |        ✔         |    ✔     |      |
| STM32F4     |  ✔   |      ✔       |      ✔      |        ✔         |    ✔     |      |
| STM32H5     |  ✔   |      ✔       |      ✔      |        ✔         |          |      |

## Build and Flash

TinyUF2 can be built either with the legacy per-port makefiles or with the new PlatformIO-based workflow (currently focused on ESP32-Sx targets). Choose the path that matches your toolchain and hardware.

### Clone

Clone this repo with its submodule

```
git clone git@github.com:adafruit/tinyuf2.git tinyuf2
cd tinyuf2
git submodule update --init
```

### PlatformIO (ESP32-Sx)

The PlatformIO project wraps the ESP-IDF build so you can generate all TinyUF2 artifacts with a single command.

1. Install the [PlatformIO Core CLI](https://docs.platformio.org/en/latest/core/installation.html).
2. Clone this repository (see the commands above) and install submodules.
3. Run the desired PlatformIO environment:

  ```
  pio run -e generic_esp32s2
  pio run -e generic_esp32s3
  ```

  Each environment forwards the board name into the ESP-IDF build and writes outputs under `build/<board>/`.

4. Use the custom helper targets for common tasks:

  ```
  pio run -e generic_esp32s3 -t tinyuf2-clean   # idf.py fullclean
  pio run -e generic_esp32s3 -t tinyuf2         # idf.py build
  pio run -e generic_esp32s3 -t tinyuf2-flash   # idf.py flash (uses ESP-IDF esptool)
  ```

Artifacts such as `tinyuf2.bin`, `combined.bin`, and the UF2 updater application are copied into `build/<board>/artifacts/`. The build also emits `flash_args`, `bootloader.bin`, and optional OTA images ready for esptool.

PlatformIO automatically launches the ESP-IDF python virtual environment, so no additional manual activation is required. If you need to adjust `sdkconfig` values, edit the board-specific file in `ports/espressif/boards/<board>/sdkconfig` before rebuilding.

### Traditional make-based flow

The original makefiles remain available for the other microcontroller families.

Firstly we need to get all submodule dependency for our board using `tools/get_deps.py` script with either family input or using --board option. You only need to do this once for each family

```
python tools/get_deps.py stm32f4
python tools/get_deps.py --board feather_stm32f405_express
```

To build this for a specific board, we need to change current directory to its port folder

```
cd ports/stm32f4
```

Then compile with `all` target:

```
make BOARD=feather_stm32f405_express all
```

### Flash (make)

`flash` target will use the default on-board debugger (jlink/cmsisdap/stlink/dfu) to flash the binary, please install those support software in advance. Some board use bootloader/DFU via serial which is required to pass to make command

```
make BOARD=feather_stm32f405_express flash
```

If you use an external debugger, there is `flash-jlink`, `flash-stlink`, `flash-pyocd` which are mostly like to work out of the box for most of the supported board.

### Debug (make)

To compile for debugging add `DEBUG=1`, this will mostly change the compiler optimization

```
make BOARD=feather_stm32f405_express DEBUG=1 all
```

#### Log

Should you have an issue running example and/or submitting an bug report. You could enable TinyUSB built-in debug logging with optional `LOG=`.
- **LOG=1** will print message from bootloader and error if any from TinyUSB stack.
- **LOG=2** and **LOG=3** will print more information with TinyUSB stack events

```
make BOARD=feather_stm32f405_express LOG=1 all
```

#### Logger

By default log message is printed via on-board UART which is slow and take lots of CPU time comparing to USB speed. If your board support on-board/external debugger, it would be more efficient to use it for logging. There are 2 protocols:

- `LOGGER=rtt`: use [Segger RTT protocol](https://www.segger.com/products/debug-probes/j-link/technology/about-real-time-transfer/)
  - Cons: requires jlink as the debugger.
  - Pros: work with most if not all MCUs
  - Software viewer is JLink RTT Viewer/Client/Logger which is bundled with JLink driver package.

```
make BOARD=feather_stm32f405_express LOG=2 LOGGER=rtt all
```
