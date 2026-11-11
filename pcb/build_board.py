"""Builds coin-light-board.kicad_pcb from scratch.

Run with KiCad's own Python:
  ~/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3 build_board.py

The board is small enough that this file is the design: every part position,
net and trace is listed here in millimeters, origin at the board's top-left.
"""

import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTPRINTS = os.path.expanduser(
    "~/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"
)
OUT = os.path.join(HERE, "coin-light-board.kicad_pcb")

BOARD_W, BOARD_H = 69.0, 23.0

POWER_W, GND_W, SIGNAL_W = 0.5, 0.4, 0.25
VIA_D, VIA_DRILL = 0.6, 0.3

# ref: (library, footprint, value, x, y, rotation, {pad: net})
PARTS = {
    # Lower cell. Its + tabs feed the chip (3 V). Its - pad is ground.
    "BT1": ("Battery", "BatteryHolder_Keystone_3034_1x20mm", "CR2032",
            12.5, 11.5, 0, {"1": "VMID", "2": "GND"}),
    # Upper cell, stacked on the lower one. Its + tabs are the 6 V LED rail.
    "BT2": ("Battery", "BatteryHolder_Keystone_3034_1x20mm", "CR2032",
            56.5, 11.5, 0, {"1": "VLED", "2": "VMID"}),
    "U1": ("Package_SO", "SOIC-8_3.9x4.9mm_P1.27mm", "ATtiny202",
           31.5, 11.5, 90,
           {"1": "VMID", "2": "BTN", "4": "PA1", "5": "PA2", "6": "UPDI", "8": "GND"}),
    "C1": ("Capacitor_SMD", "C_0603_1608Metric", "100nF",
           27.6, 11.5, 90, {"1": "VMID", "2": "GND"}),
    # Blue channel, upper half of the strip.
    "R4": ("Resistor_SMD", "R_0603_1608Metric", "10k",
           35.85, 9.02, 0, {"1": "PA2", "2": "B2"}),
    "Q2": ("Package_TO_SOT_SMD", "SOT-23", "MMBT3904",
           39.5, 9.97, 0, {"1": "B2", "2": "GND", "3": "C2"}),
    "D2": ("LED_SMD", "LED_0805_2012Metric", "blue",
           40.44, 6.3, 90, {"1": "C2", "2": "D2A"}),
    "R2": ("Resistor_SMD", "R_0603_1608Metric", "620",
           37.6, 5.36, 0, {"1": "VLED", "2": "D2A"}),
    # Red channel, lower half of the strip.
    "R3": ("Resistor_SMD", "R_0603_1608Metric", "10k",
           35.85, 13.98, 0, {"1": "PA1", "2": "B1"}),
    "Q1": ("Package_TO_SOT_SMD", "SOT-23", "MMBT3904",
           39.5, 14.93, 0, {"1": "B1", "2": "GND", "3": "C1"}),
    "D1": ("LED_SMD", "LED_0805_2012Metric", "red",
           40.44, 18.6, 270, {"1": "C1", "2": "D1A"}),
    "R1": ("Resistor_SMD", "R_0603_1608Metric", "820",
           37.6, 19.54, 0, {"1": "VLED", "2": "D1A"}),
    # Solder pads for LEDs on wires, in parallel with D1 and D2.
    "J1": ("Connector_Wire", "SolderWirePad_1x01_SMD_1x2mm", "BLUE+",
           42.6, 5.36, 0, {"1": "D2A"}),
    "J2": ("Connector_Wire", "SolderWirePad_1x01_SMD_1x2mm", "BLUE-",
           42.6, 9.97, 0, {"1": "C2"}),
    "J3": ("Connector_Wire", "SolderWirePad_1x01_SMD_1x2mm", "RED-",
           42.6, 14.93, 0, {"1": "C1"}),
    "J4": ("Connector_Wire", "SolderWirePad_1x01_SMD_1x2mm", "RED+",
           42.6, 19.54, 0, {"1": "D1A"}),
    # Programming pads, 3 mm apart.
    "TP1": ("TestPoint", "TestPoint_Pad_D1.5mm", "GND",
            26.14, 5.2, 0, {"1": "GND"}),
    "TP2": ("TestPoint", "TestPoint_Pad_D1.5mm", "VDD",
            29.14, 5.2, 0, {"1": "VMID"}),
    "TP3": ("TestPoint", "TestPoint_Pad_D1.5mm", "UPDI",
            32.14, 5.2, 0, {"1": "UPDI"}),
    "SW1": ("Button_Switch_SMD", "SW_Push_1P1T_XKB_TS-1187A", "TS-1187A",
            30.3, 19.0, 0, {"1": "BTN", "2": "GND"}),
}

# net: [(width, [points...])]. Every trace is on the top layer.
TRACES = {
    "VMID": [
        # Runs along the top edge: joins both + tabs of BT1 to the - pad of BT2.
        (POWER_W, [(1.51, 11.5), (1.51, 1.3), (56.5, 1.3), (56.5, 4.0)]),
        (POWER_W, [(23.48, 11.5), (23.48, 1.3)]),
        (POWER_W, [(23.48, 13.97), (29.59, 13.97)]),
        (POWER_W, [(27.6, 12.28), (27.6, 13.97)]),
        (POWER_W, [(29.14, 5.2), (29.14, 1.3)]),
    ],
    "VLED": [
        # Runs along the bottom edge: joins both + tabs of BT2 and feeds R1, R2.
        (POWER_W, [(36.77, 5.36), (36.77, 3.3), (45.52, 3.3), (45.52, 21.7)]),
        (POWER_W, [(36.77, 19.54), (36.77, 21.7), (67.48, 21.7), (67.48, 11.5)]),
    ],
    "GND": [
        (GND_W, [(26.14, 5.2), (26.14, 9.03), (29.59, 9.03)]),
        (GND_W, [(27.6, 10.72), (27.6, 9.03)]),
        (GND_W, [(38.56, 10.92), (38.56, 12.3)]),
        (GND_W, [(38.56, 15.88), (38.56, 17.1)]),
        (GND_W, [(12.5, 19.5), (12.5, 21.75)]),
        (GND_W, [(15.0, 19.5), (15.0, 21.75)]),
        (GND_W, [(27.3, 20.88), (25.9, 20.88)]),
        (GND_W, [(33.3, 20.88), (34.7, 20.88)]),
    ],
    "PA2": [(SIGNAL_W, [(33.41, 9.03), (35.02, 9.02)])],
    "B2": [(SIGNAL_W, [(36.67, 9.02), (38.56, 9.02)])],
    "C2": [(SIGNAL_W, [(40.44, 7.24), (40.44, 9.97), (42.6, 9.97)])],
    "D2A": [(SIGNAL_W, [(38.43, 5.36), (42.6, 5.36)])],
    "PA1": [(SIGNAL_W, [(33.41, 13.97), (35.02, 13.98)])],
    "B1": [(SIGNAL_W, [(36.67, 13.98), (38.56, 13.98)])],
    "C1": [(SIGNAL_W, [(40.44, 17.66), (40.44, 14.93), (42.6, 14.93)])],
    "D1A": [(SIGNAL_W, [(38.43, 19.54), (42.6, 19.54)])],
    "UPDI": [(SIGNAL_W, [(32.13, 5.2), (32.13, 9.03)])],
    "BTN": [
        (SIGNAL_W, [(27.3, 17.12), (27.3, 15.7), (33.3, 15.7), (33.3, 17.12)]),
        (SIGNAL_W, [(30.86, 13.97), (30.86, 15.7)]),
    ],
}
# (net, x, y) drops to the ground plane on the bottom layer.
VIAS = [
    ("GND", 26.14, 7.6),
    ("GND", 38.56, 12.3),
    ("GND", 38.56, 17.1),
    ("GND", 12.5, 21.75),
    ("GND", 15.0, 21.75),
    ("GND", 25.9, 20.88),
    ("GND", 34.7, 20.88),
]
# (text, x, y)
LABELS = [
    ("GND", 26.14, 3.2),
    ("3V", 29.14, 3.2),
    ("UPDI", 32.4, 3.2),
    ("B+", 44.0, 5.36),
    ("B-", 44.0, 9.97),
    ("R-", 44.0, 14.93),
    ("R+", 44.0, 19.54),
    ("REV A", 30.3, 22.45),
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

    for ref, (lib, name, value, x, y, rot, pads) in PARTS.items():
        fp = pcbnew.FootprintLoad(os.path.join(FOOTPRINTS, lib + ".pretty"), name)
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
        fp.SetOrientationDegrees(rot)
        for pad in fp.Pads():
            if pad.GetNumber() in pads:
                pad.SetNet(net(pads[pad.GetNumber()]))
        if "--pads" in sys.argv:
            for pad in fp.Pads():
                p, s = pad.GetPosition(), pad.GetBoundingBox()
                print(f"{ref}.{pad.GetNumber():3} {pad.GetNetname():5} "
                      f"({pcbnew.ToMM(p.x):6.2f},{pcbnew.ToMM(p.y):6.2f}) "
                      f"x {pcbnew.ToMM(s.GetLeft()):.2f}..{pcbnew.ToMM(s.GetRight()):.2f} "
                      f"y {pcbnew.ToMM(s.GetTop()):.2f}..{pcbnew.ToMM(s.GetBottom()):.2f}")
            c = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
            print(f"{ref} courtyard x {pcbnew.ToMM(c.GetLeft()):.2f}..{pcbnew.ToMM(c.GetRight()):.2f} "
                  f"y {pcbnew.ToMM(c.GetTop()):.2f}..{pcbnew.ToMM(c.GetBottom()):.2f}")

    for name, runs in TRACES.items():
        for width, points in runs:
            for a, b in zip(points, points[1:]):
                track = pcbnew.PCB_TRACK(board)
                track.SetStart(pt(*a))
                track.SetEnd(pt(*b))
                track.SetWidth(mm(width))
                track.SetLayer(pcbnew.F_Cu)
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

    outline = pcbnew.PCB_SHAPE(board)
    outline.SetShape(pcbnew.SHAPE_T_RECT)
    outline.SetStart(pt(0, 0))
    outline.SetEnd(pt(BOARD_W, BOARD_H))
    outline.SetLayer(pcbnew.Edge_Cuts)
    outline.SetWidth(mm(0.1))
    board.Add(outline)

    # Solid ground plane on the bottom layer.
    zone = pcbnew.ZONE(board)
    zone.SetLayer(pcbnew.B_Cu)
    zone.SetNet(net("GND"))
    zone.SetZoneName("GND")
    poly = zone.Outline()
    poly.NewOutline()
    for x, y in ((0, 0), (BOARD_W, 0), (BOARD_W, BOARD_H), (0, BOARD_H)):
        poly.Append(mm(x), mm(y))
    board.Add(zone)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())

    for text, x, y in LABELS:
        label = pcbnew.PCB_TEXT(board)
        label.SetText(text)
        label.SetPosition(pt(x, y))
        label.SetLayer(pcbnew.F_SilkS)
        label.SetTextSize(pcbnew.VECTOR2I(mm(0.8), mm(0.8)))
        label.SetTextThickness(mm(0.12))
        board.Add(label)

    pcbnew.SaveBoard(OUT, board)
    print("wrote", OUT)


main()
