# How to order test boards from JLCPCB

This is the order for the first test: two orders of 5 boards each. One order ships to the coin factory and one ships to us. JLCPCB sends one order to one address, so it takes two orders.

Nobody has placed this order yet. The steps below describe what to choose. JLCPCB's screens may use slightly different words.

## Files to upload

| File | Where JLCPCB asks for it |
| --- | --- |
| `pcb/coin-light-board-gerbers.zip` | The first upload, for the bare board |
| `pcb/jlcpcb-bom.csv` | "BOM" in the assembly step |
| `pcb/jlcpcb-cpl.csv` | "CPL" or "Pick and Place" in the assembly step |
| `firmware/firmware.hex` | Sent with the programming request |

## Board options

| Option | Choice |
| --- | --- |
| Layers | 2 |
| Size | 75 × 27.4 mm. JLCPCB reads it from the file. |
| Quantity | 5 |
| Thickness | 0.8 mm. A thinner board leaves more depth in the coin. |
| Surface finish | Lead-free HASL |
| Everything else | Leave as JLCPCB sets it |

## Assembly options

| Option | Choice |
| --- | --- |
| PCB Assembly | On |
| Assembly type | Standard. The cheaper Economic type places one side only. |
| Sides | Both sides |
| Quantity | 5 |

Every part in `pcb/jlcpcb-bom.csv` has a JLCPCB part number:

| Ref | Part | JLCPCB part | Side |
| --- | --- | --- | --- |
| U1 | ATtiny202-SSNR | C2052951 | Back |
| Q1, Q2 | MMBT3904 | C20526 | Back |
| R3, R4 | 10 kΩ, 0603 | C25804 | Back |
| R1 | 820 Ω, 0603 | C23253 | Back |
| R2 | 620 Ω, 0603 | C23220 | Back |
| C1 | 100 nF, 0603 | C14663 | Back |
| SW1 | TS-1102S-C-C-B push button, 6 × 6 × 5 mm | C381039 | Back |
| BT1, BT2 | MY-2032-08-R battery holder | C964832 | Back |
| D1 | NCD0805R1 red LED, 0805 | C84256 | Front |
| D2 | KT-0805B blue LED, 0805 | C2293 | Front |

If JLCPCB says a part is out of stock, stop and choose a replacement before paying. The battery holder and the chip are the two to watch.

## Check the placement preview

JLCPCB shows a picture of where each part will go. KiCad and JLCPCB do not always agree on which way a part faces, so check these before paying. JLCPCB calls the back side "Top" and the front side "Bottom".

- **D1 and D2 (the LEDs, on the Bottom side).** Each LED stands upright, with its two pads above and below each other. The cathode mark must be on the pad nearer the long straight edge, the edge with no tab.
- **U1 (the chip).** The pin 1 dot must be at the corner nearest C1 and nearest the tab with the button.
- **Q1 and Q2.** The single pin of each transistor must sit on the single pad.
- **BT1 and BT2.** Each holder must sit over its three pads: one round pad in the middle and one long pad at each end.

If a part is turned the wrong way, rotate it in the preview.

## Ask JLCPCB to load the firmware

Standard assembly has a programming or function-test option. Ask for it, attach `firmware/firmware.hex`, and give them this:

> Please program U1 on every board. Chip: ATtiny202. Interface: UPDI, one wire. The three programming pads are on the Bottom side, marked UPDI, 3V and GND. Power the board through the 3V pad at 3.3 V. No batteries are fitted. File: firmware.hex. Fuses: leave at factory default.

**Not confirmed:** JLCPCB does not publish which chips it can program. If they say no, place the order anyway. The boards that come to us can be loaded by hand. The boards that go to the factory will not light, but they still show whether the board fits the coin.

## Batteries

JLCPCB does not supply batteries. Each board needs 2 × CR2032. Put each battery in with its `+` side up, facing away from the board.

## The two orders

| Order | Ship to | What it is for |
| --- | --- | --- |
| 1 | Us | Load the firmware if needed, watch it flash, measure the battery drain, adjust brightness |
| 2 | The coin factory | Put a board in a sample coin: does it fit, do the LEDs sit under the windows, does the button reach the back |

**Not confirmed:** whether JLCPCB's international site ships to an address in mainland China.

## Loading the firmware by hand

For boards that arrive without firmware. This has not been tried yet.

1. Take both batteries out.
2. Connect a UPDI programmer to the three pads on the front side: UPDI, 3V and GND. A USB serial adapter set to 3.3 V, wired as "SerialUPDI", is the cheapest kind.
3. Run:

```sh
pymcuprog write -t uart -u /dev/tty.usbserial-XXXX -d attiny202 -f firmware/firmware.hex
```

Replace `/dev/tty.usbserial-XXXX` with the adapter's port name.

## What changes for the full run

- The button. The test uses a 5 mm tall button. The final height depends on how thick the back of the coin is.
- The resistors R1 and R2, if the test shows the red and blue are not equally bright.
- The quantity: 800 boards for 760 coins.
