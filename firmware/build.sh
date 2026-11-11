#!/bin/sh
# Compiles the firmware in Docker. PlatformIO's AVR compiler has no Apple
# silicon build, so it cannot run on this Mac directly.
# Output: firmware.hex, the file to load onto the chip.
cd "$(dirname "$0")" && docker run --rm -v "$PWD":/fw -w /fw \
	-e PLATFORMIO_CORE_DIR=/fw/.pio-core python:3.13-slim \
	sh -c "pip install -q --root-user-action=ignore platformio && pio run" &&
	cp .pio/build/attiny202/firmware.hex firmware.hex
