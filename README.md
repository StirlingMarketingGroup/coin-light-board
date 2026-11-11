# Coin Light Board

A small circuit board that goes inside a metal challenge coin. Press the button and a red light and a blue light flash in turn, like a police light. Press again and the lights stop.

![Top view of the board](docs/board.png)

## Status

**Revision A. Designed, not built.** The layout passes KiCad's design-rule check and the firmware compiles. No board has been made or tested yet.

## What it does

- Press the button: red is on for 250 ms, then blue is on for 250 ms. This repeats. That is 2 cycles each second.
- Press the button again: both lights turn off.
- After 60 seconds the lights turn off on their own. This saves the battery if a coin is left on.
- When the lights are off, the chip sleeps and uses almost no power.

## Size and fit

| | |
| --- | --- |
| Board | 69 mm long, 23 mm wide |
| Height with batteries | about 6 mm (estimate) |
| Batteries | 2 × CR2032 |
| Lights | 1 red LED and 1 blue LED on the board, or on wires |
| Button | On the board, or on wires |

All parts are on one side of the board.

**Lights on wires.** The four pads marked `B+`, `B-`, `R-`, `R+` are for LEDs on short wires. Use them when the light holes in the coin are not above the LEDs on the board. Use the LED on the board or the LED on wires for each color, never both.

**Button on wires.** The button on the board is 1.5 mm tall. If the coin has its own button, solder its two wires to the pads of `SW1`.

**Batteries.** Each holder has a `+` mark. Put each battery in with its `+` side up, facing away from the board.

## The circuit

![Circuit drawing](docs/schematic.svg)

**Why two batteries.** A red LED needs about 2 V. A blue LED needs about 3 V. One 3 V coin battery is not enough for the blue LED when the battery gets older. Two batteries in series give 6 V for the LEDs. The chip uses only the lower battery, so the board needs no voltage regulator.

**Why two transistors.** Each LED has its own transistor and its own resistor. A red LED and a blue LED that share one output do not both light, because the red LED holds the voltage too low for the blue one.

## Parts

| Ref | Part | JLCPCB part | Note |
| --- | --- | --- | --- |
| U1 | ATtiny202-SSNR, SOIC-8 | C2052951 | ATtiny402, 212 and 412 fit the same pads and run the same firmware. |
| Q1, Q2 | MMBT3904, SOT-23 | C20526 | |
| R3, R4 | 10 kΩ, 0603 | C25804 | Confirm the part number on JLCPCB. |
| C1 | 100 nF, 0603 | C14663 | Confirm the part number on JLCPCB. |
| R1 | 820 Ω, 0603 | choose at order | Sets the red brightness, about 5 mA. |
| R2 | 620 Ω, 0603 | choose at order | Sets the blue brightness, about 5 mA. |
| D1, D2 | Red LED and blue LED, 0805 | choose at order | |
| SW1 | TS-1187A-B-A-B push button | C318884 | |
| BT1, BT2 | CR2032 holder, Keystone 3034 pads | not matched yet | Not in the JLCPCB placement file. Solder by hand. |

## Files

| File | What it is |
| --- | --- |
| `pcb/coin-light-board.kicad_pcb` | The board. Open it in KiCad 10. |
| `pcb/build_board.py` | The script that draws the board. Every part position and trace is listed in it. |
| `pcb/export.sh` | Rebuilds the board, checks it, and writes the factory files. |
| `pcb/coin-light-board-gerbers.zip` | Gerber and drill files for the bare board. |
| `pcb/jlcpcb-bom.csv`, `pcb/jlcpcb-cpl.csv` | Parts list and placement file for JLCPCB assembly. |
| `firmware/src/main.c` | The firmware, about 60 lines of C. |
| `firmware/build.sh` | Compiles the firmware in Docker. |

## Build

Firmware, with Docker running:

```sh
firmware/build.sh
```

The file for the chip is `firmware/.pio/build/attiny202/firmware.hex`. Load it through the `GND`, `3V` and `UPDI` pads with a UPDI programmer. **Take both batteries out first.** A programmer that powers the `3V` pad would push current into the lower battery.

Board files, with KiCad 10 in `~/Applications/KiCad`:

```sh
pcb/export.sh
```

## Known gaps

- Nothing has been built. The LED resistor values come from calculation. They need tuning on a real board.
- The lower battery also runs the chip, so it drains a little faster than the upper one while the lights flash.
- If something holds the button down, the chip sleeps, but its pull-up resistor still draws about 0.1 mA. That would empty the lower battery in about three months.
- Nothing protects the board from a battery put in upside down.
- There is no schematic file. The circuit drawing above and `build_board.py` are the design.
- The rotations in the JLCPCB placement file may need correcting in JLCPCB's preview.

## License

MIT. See [LICENSE](LICENSE). The board design and the firmware are both covered.

## Made by

[Signature Coins](https://signaturecoins.com), a Stirling Marketing Group brand.
