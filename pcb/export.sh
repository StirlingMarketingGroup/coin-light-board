#!/bin/sh
# Rebuilds the board from build_board.py, checks it, and writes every file a
# board factory needs. Needs KiCad 10 in ~/Applications/KiCad.
set -eu
cd "$(dirname "$0")"
KICAD="$HOME/Applications/KiCad/KiCad.app/Contents"
CLI="$KICAD/MacOS/kicad-cli"
BOARD=coin-light-board.kicad_pcb

"$KICAD/Frameworks/Python.framework/Versions/Current/bin/python3" build_board.py

# Stops here when the board has an electrical error or an unconnected pad.
"$CLI" pcb drc --severity-error --exit-code-violations -o drc.rpt "$BOARD"
rm drc.rpt

rm -rf gerbers coin-light-board-gerbers.zip && mkdir gerbers
"$CLI" pcb export gerbers -o gerbers/ --no-x2 --subtract-soldermask \
	--layers F.Cu,B.Cu,F.Paste,F.SilkS,B.SilkS,F.Mask,B.Mask,Edge.Cuts "$BOARD"
"$CLI" pcb export drill -o gerbers/ --format excellon --excellon-units mm "$BOARD"
(cd gerbers && zip -q ../coin-light-board-gerbers.zip ./*)

# JLCPCB's placement file. The battery holders are left out: they are
# soldered by hand until a holder JLCPCB stocks is matched to the pads.
"$CLI" pcb export pos -o pos.csv --format csv --units mm --side front "$BOARD"
{
	echo "Designator,Mid X,Mid Y,Layer,Rotation"
	tail -n +2 pos.csv | grep -v '^"BT' |
		awk -F, '{ gsub(/"/, "", $1); printf "%s,%.3fmm,%.3fmm,Top,%d\n", $1, $4, $5, $6 }'
} > jlcpcb-cpl.csv
rm pos.csv

"$CLI" pcb render --side top --width 1800 --height 640 --zoom 2.35 \
	--background opaque -o ../docs/board.png "$BOARD"
