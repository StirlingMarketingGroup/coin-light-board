"""Builds coin-light-board.kicad_pcb from scratch. Revision B.

Run with KiCad's own Python (pcb/export.sh does this):
  ~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 build_board.py

The board is small enough that this file is the design: every part position,
net and trace is listed here in millimeters, origin at the board's top-left.

The board has two sides:
  BACK  (KiCad front copper): batteries, chip, button. Faces the back of the coin.
  FRONT (KiCad back copper):  the two LEDs and the programming pads. Faces the
                              front of the coin, with one LED under each light window.
All coordinates are as seen from the BACK side.
"""

import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTPRINTS = os.path.expanduser(
    "~/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
OUT = os.path.join(HERE, "coin-light-board.kicad_pcb")

BACK, FRONT = pcbnew.F_Cu, pcbnew.B_Cu

# The main board is 75 x 22 mm. A tab below the middle carries the button.
BOARD_W, BOARD_H = 75.0, 22.0
TAB_X0, TAB_X1, TAB_Y1 = 31.4, 43.8, 27.4
OUTLINE = [
    (0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (TAB_X1, BOARD_H),
    (TAB_X1, TAB_Y1), (TAB_X0, TAB_Y1), (TAB_X0, BOARD_H), (0, BOARD_H),
]

# The light windows in the coin are 68.35 mm apart and 6.86 mm below the top
# edge of the board. One LED sits under the middle of each window.
LED_Y = 6.86
RED_X = BOARD_W / 2 - 68.35 / 2
BLUE_X = BOARD_W / 2 + 68.35 / 2
LED_K_Y, LED_A_Y = LED_Y - 0.94, LED_Y + 0.94

POWER_W, GND_W, SIGNAL_W = 0.5, 0.4, 0.25
VIA_D, VIA_DRILL = 0.6, 0.3

LED = ("LED_SMD", "LED_0805_2012Metric")
RES = ("Resistor_SMD", "R_0603_1608Metric")
NPN = ("Package_TO_SOT_SMD", "SOT-23")
# Footprints from JLCPCB's own library, kept in lib.pretty next to this file.
HOLDER = ("lib", "BAT-SMD_MY-2032-08")
BUTTON = ("lib", "KEY-SMD_4P-L6.0-W6.0-P4.50-LS8.6")
PAD = ("TestPoint", "TestPoint_Pad_D1.5mm")

# ref: (side, (library, footprint), value, x, y, rotation, {pad: net})
PARTS = {
    # Lower cell. Its + tabs feed the chip (3 V). Its - pad is ground.
    "BT1": (BACK, HOLDER, "CR2032", 18.5, 11.0, 0, {"1": "VMID", "2": "GND"}),
    # Upper cell, stacked on the lower one. Its + tabs are the 6 V LED rail.
    "BT2": (BACK, HOLDER, "CR2032", 56.5, 11.0, 0, {"1": "VLED", "2": "VMID"}),
    "U1": (BACK, ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm"), "ATtiny202", 35.0, 11.0, 90,
           {"1": "VMID", "2": "BTN", "4": "PA1", "5": "PA2", "6": "UPDI", "8": "GND"}),
    "C1": (BACK, ("Capacitor_SMD", "C_0603_1608Metric"), "100nF", 31.4, 11.0, 90,
           {"1": "VMID", "2": "GND"}),
    # Blue channel, above the chip.
    "R4": (BACK, RES, "10k", 36.91, 5.6, 90, {"1": "PA2", "2": "B2"}),
    "Q2": (BACK, NPN, "MMBT3904", 40.6, 4.2, 0, {"1": "B2", "2": "GND", "3": "C2"}),
    "R2": (BACK, RES, "620", 41.54, 7.6, 90, {"1": "BK", "2": "C2"}),
    # Red channel, below the chip.
    "R3": (BACK, RES, "10k", 36.91, 16.4, 270, {"1": "PA1", "2": "B1"}),
    "Q1": (BACK, NPN, "MMBT3904", 40.6, 17.8, 0, {"1": "B1", "2": "GND", "3": "C1"}),
    "R1": (BACK, RES, "820", 41.54, 14.4, 90, {"1": "C1", "2": "RK"}),
    # 6 x 6 mm push button on the tab. Its stem height is chosen to reach
    # through the back of the coin. Only two diagonal pads are wired: in a
    # four-pad button, diagonal pads are always on opposite contacts.
    "SW1": (BACK, BUTTON, "6x6 tact", 37.6, 23.7, 0, {"1": "BTN", "4": "GND"}),
    # LEDs on the front side, one under each light window. Pad 1 is the cathode.
    "D1": (FRONT, LED, "red", RED_X, LED_Y, 270, {"1": "RK", "2": "VLED"}),
    "D2": (FRONT, LED, "blue", BLUE_X, LED_Y, 270, {"1": "BK", "2": "VLED"}),
    # Programming pads on the front side, 2.54 mm apart, between the chip's pin rows.
    "TP1": (FRONT, PAD, "GND", 30.55, 11.0, 0, {"1": "GND"}),
    "TP2": (FRONT, PAD, "VDD", 33.09, 11.0, 0, {"1": "VMID"}),
    "TP3": (FRONT, PAD, "UPDI", 35.63, 11.0, 0, {"1": "UPDI"}),
}

# (net, side, width, [points...])
TRACES = [
    # 3 V: BT1's right tab to the capacitor and the chip.
    ("VMID", BACK, POWER_W, [(29.38, 11.78), (31.4, 11.78), (31.4, 13.47), (33.09, 13.47)]),
    # 3 V: BT1's two tabs, joined on the front side, then on to BT2's round
    # - pad. No trace runs under a battery on the back side: the rim of a
    # coin cell is its + side and must touch nothing but solder mask.
    ("VMID", BACK, POWER_W, [(7.62, 13.0), (7.62, 14.6)]),
    ("VMID", BACK, POWER_W, [(29.38, 13.0), (29.38, 14.6)]),
    ("VMID", FRONT, POWER_W, [(7.62, 14.6), (43.2, 14.6), (43.2, 13.3), (56.5, 13.3), (56.5, 10.0)]),
    # 3 V to its programming pad.
    ("VMID", BACK, SIGNAL_W, [(33.09, 13.47), (33.09, 11.0)]),
    # 6 V: BT2's two tabs drop to a rail on the front side that reaches both LED anodes.
    ("VLED", BACK, POWER_W, [(45.62, 13.0), (45.62, 14.6)]),
    ("VLED", BACK, POWER_W, [(67.38, 13.0), (67.38, 14.6)]),
    ("VLED", FRONT, POWER_W, [(45.62, 14.6), (45.62, 16.0)]),
    ("VLED", FRONT, POWER_W, [(67.38, 14.6), (67.38, 16.0)]),
    ("VLED", FRONT, POWER_W, [(RED_X, LED_A_Y), (RED_X, 16.0), (BLUE_X, 16.0), (BLUE_X, LED_A_Y)]),
    # Ground.
    ("GND", BACK, GND_W, [(31.4, 10.22), (31.4, 8.53), (33.09, 8.53)]),
    ("GND", BACK, GND_W, [(31.4, 8.53), (31.4, 7.0)]),
    ("GND", BACK, GND_W, [(39.66, 5.15), (39.66, 7.0)]),
    ("GND", BACK, GND_W, [(39.66, 18.75), (39.66, 20.2)]),
    ("GND", BACK, GND_W, [(41.9, 25.95), (40.2, 25.95)]),
    # Blue channel.
    ("PA2", BACK, SIGNAL_W, [(36.91, 8.53), (36.91, 6.42)]),
    ("B2", BACK, SIGNAL_W, [(36.91, 4.78), (36.91, 3.25), (39.66, 3.25)]),
    ("C2", BACK, SIGNAL_W, [(41.54, 4.2), (41.54, 6.78)]),
    ("BK", BACK, SIGNAL_W, [(41.54, 8.42), (41.54, 9.7)]),
    ("BK", FRONT, SIGNAL_W, [(41.54, 9.7), (41.54, LED_K_Y), (BLUE_X, LED_K_Y)]),
    # Red channel.
    ("PA1", BACK, SIGNAL_W, [(36.91, 13.47), (36.91, 15.58)]),
    ("B1", BACK, SIGNAL_W, [(36.91, 16.85), (39.66, 16.85)]),
    ("C1", BACK, SIGNAL_W, [(41.54, 17.8), (41.54, 15.22)]),
    ("RK", BACK, SIGNAL_W, [(41.54, 13.58), (41.54, 12.3)]),
    ("RK", FRONT, SIGNAL_W, [(41.54, 12.3), (38.5, 12.3), (38.5, LED_K_Y), (RED_X, LED_K_Y)]),
    # Button and programming pin.
    ("BTN", BACK, SIGNAL_W, [(34.37, 13.47), (34.37, 20.0), (33.3, 20.0), (33.3, 21.45)]),
    ("UPDI", BACK, SIGNAL_W, [(35.63, 8.53), (35.63, 11.0)]),
]

# (net, x, y) joins the two sides. GND vias land in the ground plane on the front.
VIAS = [
    ("VMID", 7.62, 14.6), ("VMID", 29.38, 14.6), ("VMID", 33.09, 11.0),
    # Inside BT2's round - pad.
    ("VMID", 56.5, 12.0), ("VMID", 56.5, 10.0),
    ("VLED", 45.62, 14.6), ("VLED", 67.38, 14.6),
    ("BK", 41.54, 9.7), ("RK", 41.54, 12.3), ("UPDI", 35.63, 11.0),
    ("GND", 31.4, 7.0), ("GND", 39.66, 7.0), ("GND", 39.66, 20.2), ("GND", 40.2, 25.95),
    # Inside BT1's round - pad.
    ("GND", 17.0, 11.0), ("GND", 20.0, 11.0),
]

# (text, side, x, y)
LABELS = [
    ("BACK", BACK, 33.3, 3.3),
    ("REV B", BACK, 33.3, 4.9),
    ("FRONT", FRONT, 37.5, 19.2),
    ("UPDI 3V GND", FRONT, 33.1, 13.3),
    ("RED", FRONT, RED_X + 3.2, LED_Y),
    ("BLUE", FRONT, BLUE_X - 3.6, LED_Y),
]


def mm(v):
    return pcbnew.FromMM(v)


def pt(x, y):
    return pcbnew.VECTOR2I(mm(x), mm(y))


def main():
    board = pcbnew.CreateEmptyBoard()
    nets = {}

    def net(name):
        if name not in nets:
            nets[name] = pcbnew.NETINFO_ITEM(board, name)
            board.Add(nets[name])
        return nets[name]

    for ref, (side, (lib, name), value, x, y, rot, pads) in PARTS.items():
        folder = HERE if lib == "lib" else FOOTPRINTS
        fp = pcbnew.FootprintLoad(os.path.join(folder, lib + ".pretty"), name)
        if fp is None:
            sys.exit(f"footprint not found: {lib}:{name}")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference(ref)
        fp.SetValue(value)
        # Reference text does not fit between parts this small. The labels
        # in LABELS mark what a person needs to find.
        fp.Reference().SetVisible(False)
        board.Add(fp)
        fp.SetPosition(pt(x, y))
        if side == FRONT:
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            if pad.GetNumber() in pads:
                pad.SetNet(net(pads[pad.GetNumber()]))
        if "--pads" in sys.argv:
            for pad in fp.Pads():
                p, s = pad.GetPosition(), pad.GetBoundingBox()
                print(f"{ref}.{pad.GetNumber():3} {pad.GetNetname():5} {'back ' if pad.IsOnLayer(BACK) else 'front'} "
                      f"({pcbnew.ToMM(p.x):6.2f},{pcbnew.ToMM(p.y):6.2f}) "
                      f"x {pcbnew.ToMM(s.GetLeft()):.2f}..{pcbnew.ToMM(s.GetRight()):.2f} "
                      f"y {pcbnew.ToMM(s.GetTop()):.2f}..{pcbnew.ToMM(s.GetBottom()):.2f}")

    for name, side, width, points in TRACES:
        for a, b in zip(points, points[1:]):
            track = pcbnew.PCB_TRACK(board)
            track.SetStart(pt(*a))
            track.SetEnd(pt(*b))
            track.SetWidth(mm(width))
            track.SetLayer(side)
            track.SetNet(net(name))
            board.Add(track)

    for name, x, y in VIAS:
        via = pcbnew.PCB_VIA(board)
        via.SetPosition(pt(x, y))
        via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        via.SetDrill(mm(VIA_DRILL))
        via.SetWidth(pcbnew.F_Cu, mm(VIA_D))
        via.SetNet(net(name))
        board.Add(via)

    for a, b in zip(OUTLINE, OUTLINE[1:] + OUTLINE[:1]):
        edge = pcbnew.PCB_SHAPE(board)
        edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
        edge.SetStart(pt(*a))
        edge.SetEnd(pt(*b))
        edge.SetLayer(pcbnew.Edge_Cuts)
        edge.SetWidth(mm(0.1))
        board.Add(edge)

    # Ground plane on the front side, around the traces there.
    zone = pcbnew.ZONE(board)
    zone.SetLayer(FRONT)
    zone.SetNet(net("GND"))
    zone.SetZoneName("GND")
    poly = zone.Outline()
    poly.NewOutline()
    for x, y in OUTLINE:
        poly.Append(mm(x), mm(y))
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    for text, side, x, y in LABELS:
        label = pcbnew.PCB_TEXT(board)
        label.SetText(text)
        label.SetPosition(pt(x, y))
        label.SetLayer(pcbnew.F_SilkS if side == BACK else pcbnew.B_SilkS)
        label.SetMirrored(side == FRONT)
        label.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        label.SetTextThickness(mm(0.12))
        board.Add(label)

    pcbnew.SaveBoard(OUT, board)
    print("wrote", OUT)


main()
