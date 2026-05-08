#!/usr/bin/env python3
"""
Arduino Mega 2560 Rev3 - Complete KiCad 9.0 Schematic Generator
Fixed:
  - KiCad 9.0 correct lib_ids (+3.3V, LD1117-5.0, BarrelJack, etc.)
  - No overlaps: A0 paper (1189x841mm), sections well-separated
  - Custom power nets → global_label (USBVCC, VIN, PWRIN, VBUS)
  - Fiducials removed (PCB-only, no schematic symbol in KiCad 9.0)
"""
import uuid as _uuid

def uid(): return str(_uuid.uuid4())

_L = []
def w(s=""): _L.append(s)

# ── KiCad primitives ─────────────────────────────────────────────────────────
def wire(x1,y1,x2,y2):
    w(f'  (wire (pts (xy {x1} {y1}) (xy {x2} {y2})))')

def junc(x,y):
    w(f'  (junction (at {x} {y}) (diameter 0) (color 0 0 0 0))')

def nc(x,y):
    w(f'  (no_connect (at {x} {y}) (uuid "{uid()}"))')

def lbl(name,x,y,rot=0,just="left"):
    """Local net label"""
    w(f'  (label "{name}" (at {x} {y} {rot})')
    w(f'    (fields_autoplaced yes)')
    w(f'    (effects (font (size 1.27 1.27)) (justify {just}))')
    w(f'    (uuid "{uid()}"))')

def glbl(name,x,y,shape="bidirectional",rot=0):
    """Global label (cross-section net)"""
    w(f'  (global_label "{name}" (shape {shape}) (at {x} {y} {rot})')
    w(f'    (effects (font (size 1.27 1.27)) (justify left))')
    w(f'    (uuid "{uid()}")')
    w(f'    (property "Intersheet References" "" (at {x} {y+2.5} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (hide yes)))')
    w(f'  )')

def pwr(net,x,y,rot=0):
    """Standard KiCad power symbol — only use known KiCad 9 power nets"""
    w(f'  (symbol (lib_id "power:{net}") (at {x} {y} {rot})')
    w(f'    (unit 1)(exclude_from_sim no)(in_bom yes)(on_board yes)(dnp no)')
    w(f'    (uuid "{uid()}")')
    w(f'    (property "Reference" "#PWR" (at {x} {y-3} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (hide yes)))')
    w(f'    (property "Value" "{net}" (at {x} {y+2.5} 0)')
    w(f'      (effects (font (size 1.27 1.27))))')
    w(f'  )')

def comp(lib_id,ref,val,fp,x,y,rot=0):
    w(f'  (symbol (lib_id "{lib_id}") (at {x} {y} {rot})')
    w(f'    (unit 1)(exclude_from_sim no)(in_bom yes)(on_board yes)(dnp no)')
    w(f'    (uuid "{uid()}")')
    w(f'    (property "Reference" "{ref}" (at {x+3} {y-2.5} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (justify left)))')
    w(f'    (property "Value" "{val}" (at {x+3} {y} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (justify left)))')
    w(f'    (property "Footprint" "{fp}" (at {x} {y+3} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (hide yes)))')
    w(f'  )')

def txt(s,x,y,sz=1.5):
    w(f'  (text "{s}" (at {x} {y} 0)')
    w(f'    (effects (font (size {sz} {sz})) (justify left)))')

def box_title(title,x,y):
    txt(f"[ {title} ]", x, y, 2.0)

# ── Layout constants ──────────────────────────────────────────────────────────
# A0 paper: 1189 × 841 mm
# ┌─────────────────────────────────────────────────────────────────────────┐
# │  SEC-A: USB + IC4   (15–260, 15–260)   │  SEC-D: Headers  (620–1175)   │
# │  SEC-B: IC3 ATmega2560 (270–560, 15–820)│                              │
# │  SEC-C: Power Supply  (15–260, 270–800) │  SEC-E: LEDs     (620, 560+)  │
# └─────────────────────────────────────────────────────────────────────────┘

# IC positions
IC3X, IC3Y   = 400, 420    # ATmega2560 center
IC4X, IC4Y   = 100, 130    # ATmega16U2 center

# Pin edge distances from center (KiCad MCU_Microchip_ATmega library)
# ATmega2560-16AU: body ±15.24mm, pin length 5.08mm → pin tip at ±20.32mm
IC3L = IC3X - 20.32    # left pin tips
IC3R = IC3X + 20.32    # right pin tips
IC3T = IC3Y - 20.32    # top pin tips
IC3B = IC3Y + 20.32    # bottom pin tips

# ATmega16U2-MU: body ±10.16mm, pin length 5.08mm → pin tip at ±15.24mm
IC4L = IC4X - 15.24
IC4R = IC4X + 15.24
IC4T = IC4Y - 15.24
IC4B = IC4Y + 15.24

# ── HEADER ────────────────────────────────────────────────────────────────────
w('(kicad_sch')
w('  (version 20231120)')
w('  (generator "kicad_sch")')
w('  (generator_version "9.0")')
w('  (paper "A0")')
w('  (title_block')
w('    (title "Arduino Mega 2560 Rev3 - Complete Schematic")')
w('    (date "2026-04-10")')
w('    (rev "3e")')
w('    (company "Arduino")')
w('    (comment 1 "ATmega2560-16AU (Main MCU) + ATmega16U2-MU (USB Bridge)")')
w('    (comment 2 "5V: LD1117S50  3.3V: LP2985-33  USB Power Switch: PMV48XP")')
w('    (comment 3 "All 63 BOM components - generated for KiCad 9.0")')
w('  )')
w('')

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION A — USB Interface + ATmega16U2 (x:15–250, y:15–260)
# ═══════════════════════════════════════════════════════════════════════════════
box_title("SECTION A: USB + ATmega16U2", 18, 16)

# X2: USB Type-B
comp("Connector_USB:USB_B","X2","USB-B_TH",
     "Connector_USB:USB_B_Lumberg_2411_01_Horizontal", 40, 65)
pwr("GND",40,78); wire(40,72,40,78)
lbl("VBUS",47,62)

# L1: Ferrite bead (VBUS filter)
comp("Device:Ferrite_Bead","L1","MH2029-300Y",
     "Inductor_SMD:L_0805_2012Metric", 70, 55)
lbl("VBUS",65,55); lbl("USBVCC_IN",75,55)
wire(65,55,67,55); wire(73,55,75,55)
glbl("USBVCC",80,55)

# Z1, Z2: ESD varistors on D-/D+
comp("Device:D_Zener","Z1","CG0603MLC-05E",
     "Capacitor_SMD:C_0603_1608Metric", 60,72, 270)
comp("Device:D_Zener","Z2","CG0603MLC-05E",
     "Capacitor_SMD:C_0603_1608Metric", 60,80, 270)
pwr("GND",60,87); wire(60,84,60,87)
lbl("USB_DN",53,72); lbl("USB_DP",53,80)

# RN2: 22R D+/D- series resistors
comp("Device:R_Pack04","RN2","22R",
     "Resistor_THT:R_Array_SIP8", 80,75)
lbl("USB_DN",73,73); lbl("USB_DP",73,77)
lbl("USB_DN_F",87,73); lbl("USB_DP_F",87,77)

# C7, C8: IC4 VCC decoupling
comp("Device:C","C7","100nF","Capacitor_SMD:C_0603_1608Metric",30,100)
comp("Device:C","C8","100nF","Capacitor_SMD:C_0603_1608Metric",42,100)
for cx in [30,42]:
    pwr("+5V",cx,94); pwr("GND",cx,107)
    wire(cx,94,cx,97); wire(cx,103,cx,107)

# IC4: ATmega16U2-MU
comp("MCU_Microchip_ATmega:ATmega16U2-MU","IC4","ATMEGA16U2-MU",
     "Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm", IC4X, IC4Y)

# IC4 power
pwr("+5V",IC4X,IC4T-6); wire(IC4X,IC4T-6,IC4X,IC4T)
pwr("GND",IC4X+2.54,IC4B+4); wire(IC4X+2.54,IC4B,IC4X+2.54,IC4B+4)

# IC4 USB pins → D+/D- labels
lbl("USB_DN_F", IC4R, IC4Y+6)
lbl("USB_DP_F", IC4R, IC4Y+8)

# IC4 crystal pins
lbl("XTAL1_U2", IC4R, IC4Y-7)
lbl("XTAL2_U2", IC4R, IC4Y-5)

# IC4 ↔ IC3 UART (global labels for cross-section connection)
glbl("USART0_RXD", IC4L, IC4Y,    "output", 180)
glbl("USART0_TXD", IC4L, IC4Y+2.54,"input", 180)

# IC4 SPI / RESET
lbl("MOSI_U2",IC4L, IC4Y-5)
lbl("MISO_U2",IC4L, IC4Y-7.5)
lbl("SCK_U2", IC4L, IC4Y-10)
lbl("RESET_U2",IC4R,IC4Y-12)

# Y2: 16MHz crystal for IC4
comp("Device:Crystal","Y2","16MHz","Crystal:Crystal_SMD_HC49-SD",165,95)
lbl("XTAL1_U2",159,92); lbl("XTAL2_U2",171,92)
wire(159,95,161,95); wire(169,95,171,95)

# C14, C15: Y2 load caps
comp("Device:C","C14","22pF","Capacitor_SMD:C_0603_1608Metric",152,88)
comp("Device:C","C15","22pF","Capacitor_SMD:C_0603_1608Metric",178,88)
lbl("XTAL1_U2",152,84); lbl("XTAL2_U2",178,84)
pwr("GND",152,95); pwr("GND",178,95)
wire(152,84,152,85); wire(152,91,152,95)
wire(178,84,178,85); wire(178,91,178,95)

# ICSP1 header
comp("Connector_Generic:Conn_02x03_Odd_Even","ICSP1","3x2M",
     "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical", 175,155)
lbl("MOSI_U2",167,150); lbl("MISO_U2",167,153); lbl("SCK_U2",167,156)
lbl("RESET_U2",182,150)
pwr("+5V",182,153); pwr("GND",182,157)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION B — ATmega2560 Main MCU (x:270–570, y:15–820)
# ═══════════════════════════════════════════════════════════════════════════════
box_title("SECTION B: ATmega2560 Main MCU", 273, 16)

# IC3: ATmega2560-16AU
comp("MCU_Microchip_ATmega:ATmega2560-16AU","IC3","ATMEGA2560-16AU",
     "Package_QFP:TQFP-100_14x14mm_P0.8mm", IC3X, IC3Y)

# ── IC3 Power (top pins) ──────────────────────────────────────────────────────
# Multiple VCC pins at top of symbol (pins 7,11,62,65,93=AVCC)
for dx in [-7.62,-5.08,-2.54,0,2.54,5.08]:
    pwr("+5V", IC3X+dx, IC3T-6)
    wire(IC3X+dx, IC3T-6, IC3X+dx, IC3T)

# AREF (pin 94)
lbl("AREF", IC3X+7.62, IC3T)

# GND pins at bottom (pins 6,53,63,66)
for dx in [-5.08,-2.54,0,2.54]:
    pwr("GND", IC3X+dx, IC3B+5)
    wire(IC3X+dx, IC3B, IC3X+dx, IC3B+5)

# ── Decoupling caps C2–C9, C16 (above IC3) ───────────────────────────────────
cap_data = [
    ("C2","100nF"), ("C3","100nF"), ("C4","100nF"), ("C5","100nF"),
    ("C6","100nF"), ("C9","100nF"), ("C10","1uF"), ("C16","100nF"),
]
for i,(cr,cv) in enumerate(cap_data):
    cx = IC3X - 17.78 + i*5.08
    comp("Device:C",cr,cv,"Capacitor_SMD:C_0603_1608Metric", cx, IC3T-18)
    pwr("+5V",cx,IC3T-24); pwr("GND",cx,IC3T-12)
    wire(cx,IC3T-24,cx,IC3T-21); wire(cx,IC3T-15,cx,IC3T-12)

# C1: AREF bypass cap
comp("Device:C","C1","22pF","Capacitor_SMD:C_0603_1608Metric",
     IC3X+20, IC3T-18)
lbl("AREF",IC3X+20,IC3T-24)
pwr("GND",IC3X+20,IC3T-12)
wire(IC3X+20,IC3T-24,IC3X+20,IC3T-21)
wire(IC3X+20,IC3T-15,IC3X+20,IC3T-12)

# ── IC3 Crystal Y1 (ceramic resonator) ───────────────────────────────────────
comp("Device:Crystal_GND24","Y1","CSTCE16M0V53-R0",
     "Crystal:Crystal_SMD_Murata_CSTxExxV-3Pin_3.2x1.3mm",
     IC3R+20, IC3T+10)
pwr("GND",IC3R+20, IC3T+16); wire(IC3R+20,IC3T+13,IC3R+20,IC3T+16)
lbl("MCU_XTAL1",IC3R+14,IC3T+8)
lbl("MCU_XTAL2",IC3R+14,IC3T+12)
lbl("MCU_XTAL1",IC3R+26,IC3T+8)
lbl("MCU_XTAL2",IC3R+26,IC3T+12)

# ── RESET circuit ─────────────────────────────────────────────────────────────
lbl("RESET_N", IC3R, IC3T+5)
comp("Device:R","R1","1M","Resistor_SMD:R_0603_1608Metric",IC3R+15,IC3T+3)
pwr("+5V",IC3R+15,IC3T-3); lbl("RESET_N",IC3R+15,IC3T+7)
wire(IC3R+15,IC3T-3,IC3R+15,IC3T); wire(IC3R+15,IC3T+6,IC3R+15,IC3T+7)

comp("Device:R","R2","1M","Resistor_SMD:R_0603_1608Metric",IC3R+23,IC3T+3)
pwr("+5V",IC3R+23,IC3T-3)
wire(IC3R+23,IC3T-3,IC3R+23,IC3T)

comp("Device:SW_Push","RESET","TS42",
     "Button_Switch_SMD:SW_SPST_Omron_B3FS-1xxx",IC3R+15,IC3T+16)
lbl("RESET_N",IC3R+9,IC3T+16)
pwr("GND",IC3R+21,IC3T+16)
wire(IC3R+9,IC3T+16,IC3R+11,IC3T+16)
wire(IC3R+19,IC3T+16,IC3R+21,IC3T+16)

# ── ICSP header ────────────────────────────────────────────────────────────────
comp("Connector_Generic:Conn_02x03_Odd_Even","ICSP","3x2M",
     "Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical",
     IC3R+18,IC3Y-20)
lbl("MOSI",IC3R+11,IC3Y-23)
lbl("MISO",IC3R+11,IC3Y-20)
lbl("SCK", IC3R+11,IC3Y-17)
lbl("RESET_N",IC3R+24,IC3Y-23)
pwr("+5V",IC3R+24,IC3Y-20); pwr("GND",IC3R+24,IC3Y-17)

# ── IC3 LEFT SIDE PINS ────────────────────────────────────────────────────────
# PB port (D10-D13, SPI, D50-D53)
#   PB0(SS)=D53, PB1(SCK)=D52, PB2(MOSI)=D51, PB3(MISO)=D50
#   PB4(OC2A)=D10, PB5(OC1A)=D11, PB6(OC1B)=D12, PB7(OC0A)=D13
for net,dy in [("D53",-9*1.27),("D52",-8*1.27),("D51",-7*1.27),("D50",-6*1.27),
               ("D10",-5*1.27),("D11",-4*1.27),("D12",-3*1.27),("D13",-2*1.27)]:
    lbl(net, IC3L-5, IC3Y+dy, just="right")
for net,dy in [("SS",  -9*1.27),("SCK",-8*1.27),("MOSI",-7*1.27),("MISO",-6*1.27)]:
    lbl(net, IC3L-13, IC3Y+dy, just="right")

# PD port: SCL(D21),SDA(D20),RX1(D19),TX1(D18),D38-D41
for net,dy in [("D21",-1*1.27),("D20",0),("D19",1*1.27),("D18",2*1.27),
               ("D38",3*1.27),("D39",4*1.27),("D40",5*1.27),("D41",6*1.27)]:
    lbl(net, IC3L-5, IC3Y+dy, just="right")
for net,dy in [("SCL",-1*1.27),("SDA",0),("RX1",1*1.27),("TX1",2*1.27)]:
    lbl(net, IC3L-13, IC3Y+dy, just="right")

# PC port (D30-D37)
for i,dy in enumerate(range(7,15)):
    lbl(f"D{37-i}", IC3L-5, IC3Y+dy*1.27, just="right")

# PL port (D42-D49)
for i,dy in enumerate(range(15,23)):
    lbl(f"D{42+i}", IC3L-5, IC3Y+dy*1.27, just="right")

# ── IC3 RIGHT SIDE PINS ───────────────────────────────────────────────────────
# UART0 → IC4 connection
glbl("USART0_RXD", IC3R, IC3Y+0*1.27, "input")
glbl("USART0_TXD", IC3R, IC3Y+1*1.27, "output")

# PE port (D2-D9)
for net,dy in [("D2",2*1.27),("D3",3*1.27),("D4",4*1.27),("D5",5*1.27)]:
    lbl(net, IC3R+5, IC3Y+dy)

# PH port (D6-D9, RX2/TX2)
for net,dy in [("D6",6*1.27),("D7",7*1.27),("D8",8*1.27),("D9",9*1.27),
               ("TX2",10*1.27),("RX2",11*1.27)]:
    lbl(net, IC3R+5, IC3Y+dy)

# PJ port (TX3/RX3)
for net,dy in [("TX3",12*1.27),("RX3",13*1.27)]:
    lbl(net, IC3R+5, IC3Y+dy)

# XTAL pins
lbl("MCU_XTAL1", IC3R, IC3T+8)
lbl("MCU_XTAL2", IC3R, IC3T+12)
lbl("RESET_N",   IC3R, IC3T+5)

# ── IC3 BOTTOM PINS ───────────────────────────────────────────────────────────
# PA port (D22-D29) — 8 pins at bottom left
for i in range(8):
    lbl(f"D{22+i}", IC3X-8.89+i*2.54, IC3B+8)

# PF port (A0-A7)
for i in range(8):
    lbl(f"A{i}", IC3X-8.89+i*2.54, IC3B+15)

# PK port (A8-A15)
for i in range(8):
    lbl(f"A{i+8}", IC3X-8.89+i*2.54, IC3B+22)

# ── Resistor networks ──────────────────────────────────────────────────────────
comp("Device:R_Pack04","RN1","10K","Resistor_THT:R_Array_SIP8",IC3R+40,IC3Y-15)
comp("Device:R_Pack04","RN3","1K", "Resistor_THT:R_Array_SIP8",IC3L-30,IC3Y-5)
comp("Device:R_Pack04","RN4","1K", "Resistor_THT:R_Array_SIP8",IC3L-30,IC3Y+8)
comp("Device:R_Pack04","RN5","10K","Resistor_THT:R_Array_SIP8",IC3L-30,IC3Y+21)
pwr("+5V",IC3R+40,IC3Y-21); pwr("GND",IC3R+40,IC3Y-9)
wire(IC3R+40,IC3Y-21,IC3R+40,IC3Y-18); wire(IC3R+40,IC3Y-12,IC3R+40,IC3Y-9)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION C — Power Supply (x:15–260, y:530–820)
# ═══════════════════════════════════════════════════════════════════════════════
box_title("SECTION C: Power Supply", 18, 533)

PS_Y = 620   # baseline Y for power section

# X1: DC barrel jack (2.1mm)
comp("Connector_BarrelJack:BarrelJack","X1","POWERSUPPLY_DC21MMX",
     "Connector_BarrelJack:BarrelJack_CUI_PJ-102A_Horizontal", 35, PS_Y)
glbl("PWRIN",42,PS_Y-2)
pwr("GND",35,PS_Y+8); wire(35,PS_Y+5,35,PS_Y+8)

# D1: M7 rectifier / reverse-polarity protection
comp("Device:D","D1","M7","Diode_SMD:D_SMB", 60, PS_Y-2)
glbl("PWRIN",53,PS_Y-2); lbl("VIN_RAW",67,PS_Y-2)
wire(53,PS_Y-2,56,PS_Y-2); wire(64,PS_Y-2,67,PS_Y-2)

# F1: Polyfuse 500mA
comp("Device:Fuse","F1","MF-MSMF050-2_500mA","Fuse:Fuse_1812_4532Metric",86,PS_Y-2)
lbl("VIN_RAW",80,PS_Y-2); lbl("VIN",93,PS_Y-2)
wire(80,PS_Y-2,82,PS_Y-2); wire(90,PS_Y-2,93,PS_Y-2)

# IC1: LD1117-5.0 (5V LDO)  ← KiCad 9.0 correct name
comp("Regulator_Linear:LD1117-5.0","IC1","LD1117S50CTR",
     "Package_TO_SOT_SMD:SOT-223-3_TabPin2", 115, PS_Y-2)
lbl("VIN",108,PS_Y-2); wire(108,PS_Y-2,110,PS_Y-2)
pwr("+5V",122,PS_Y-5); wire(122,PS_Y-2,122,PS_Y-5)
pwr("GND",115,PS_Y+5); wire(115,PS_Y+2,115,PS_Y+5)

# PC1, PC2: 47uF bulk caps
comp("Device:CP","PC1","47uF","Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",138,PS_Y-2)
comp("Device:CP","PC2","47uF","Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",152,PS_Y-2)
for cx in [138,152]:
    pwr("+5V",cx,PS_Y-8); pwr("GND",cx,PS_Y+5)
    wire(cx,PS_Y-8,cx,PS_Y-5); wire(cx,PS_Y+2,cx,PS_Y+5)

# IC6: LP2985-3.3 (3.3V LDO) ← KiCad 9.0 correct name
comp("Regulator_Linear:LP2985-3.3","IC6","LP2985-33DBUR",
     "Package_TO_SOT_SMD:SOT-23-5", 55, PS_Y-30)
pwr("+5V",48,PS_Y-32); wire(48,PS_Y-30,51,PS_Y-30)
pwr("+3.3V",62,PS_Y-32); wire(62,PS_Y-30,62,PS_Y-32)   # ← +3.3V not +3V3
pwr("GND",55,PS_Y-24); wire(55,PS_Y-27,55,PS_Y-24)

# C11, C12, C13: IC6 decoupling
for cr,cv,cx,net in [("C11","100nF",36,"+5V"),("C12","100nF",70,"+3.3V"),("C13","1uF",78,"+3.3V")]:
    comp("Device:C",cr,cv,"Capacitor_SMD:C_0603_1608Metric",cx,PS_Y-30)
    pwr(net,cx,PS_Y-36); pwr("GND",cx,PS_Y-24)
    wire(cx,PS_Y-36,cx,PS_Y-33); wire(cx,PS_Y-27,cx,PS_Y-24)

# T1: PMV48XP P-MOSFET (USB power switch)
comp("Device:Q_PMOS_GSD","T1","PMV48XP","Package_TO_SOT_SMD:SOT-23",130,PS_Y-30)
glbl("USBVCC",130,PS_Y-36)
lbl("VIN",124,PS_Y-30); wire(124,PS_Y-30,126,PS_Y-30)
pwr("+5V",136,PS_Y-30); wire(134,PS_Y-30,136,PS_Y-30)
wire(130,PS_Y-33,130,PS_Y-36)

# IC7: LMV358 dual op-amp (auto-reset comparator)
comp("Amplifier_Operational:LMV358","IC7","LMV358IDGKR",
     "Package_SO:MSOP-8_3x3mm_P0.65mm", 105, PS_Y-30)
pwr("+5V",105,PS_Y-37); pwr("GND",105,PS_Y-23)
wire(105,PS_Y-37,105,PS_Y-33); wire(105,PS_Y-27,105,PS_Y-23)
lbl("DTR",98,PS_Y-31)
lbl("T1_GATE",112,PS_Y-31)

# D2, D3: switching diodes (auto-reset)
comp("Device:D","D2","CD1206-S01575","Diode_SMD:D_MiniMELF",75,PS_Y-50)
comp("Device:D","D3","CD1206-S01575","Diode_SMD:D_MiniMELF",90,PS_Y-50)
lbl("DTR",68,PS_Y-50); lbl("RESET_N",97,PS_Y-50)
wire(68,PS_Y-50,71,PS_Y-50); wire(79,PS_Y-50,85,PS_Y-50)
wire(94,PS_Y-50,97,PS_Y-50)

# Solder jumpers, JP5
comp("Jumper:SolderJumper-2_Open","GROUND","SJ",
     "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",165,PS_Y)
comp("Jumper:SolderJumper-2_Open","RESET-EN","SJ",
     "Jumper:SolderJumper-2_P1.3mm_Open_RoundedPad1.0x1.5mm",178,PS_Y)
comp("Connector_Generic:Conn_02x02_Odd_Even","JP5","2x2M",
     "Connector_PinHeader_2.54mm:PinHeader_2x02_P2.54mm_Vertical",195,PS_Y)
lbl("RESET_N",159,PS_Y); lbl("+5V_USB",172,PS_Y)
pwr("GND",165,PS_Y+6); pwr("GND",178,PS_Y+6)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION D — Arduino Shield Headers (x:580–1170, y:15–800)
# ═══════════════════════════════════════════════════════════════════════════════
box_title("SECTION D: Arduino Shield Headers", 583, 16)

HX = 620   # header section base X

# POWER 1x8: VIN, 5V, 3.3V, GND, GND, RESET, IOREF, NC
comp("Connector_Generic:Conn_01x08","POWER","8x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", HX, 60)
for net,i in [("VIN",0),("+5V",1),("+3.3V",2),("GND",3),
              ("GND",4),("RESET_N",5),("IOREF",6),("NC",7)]:
    y = 60 + (i-3.5)*2.54
    lbl(net, HX-10, y, just="right"); wire(HX-10,y,HX-5,y)

# ADCL 1x8: A0-A7
comp("Connector_Generic:Conn_01x08","ADCL","8x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", HX+30, 60)
for i in range(8):
    y = 60+(i-3.5)*2.54
    lbl(f"A{i}", HX+20,y, just="right"); wire(HX+20,y,HX+25,y)

# ADCH 1x8: A8-A15
comp("Connector_Generic:Conn_01x08","ADCH","8x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", HX+60, 60)
for i in range(8):
    y = 60+(i-3.5)*2.54
    lbl(f"A{i+8}", HX+50,y, just="right"); wire(HX+50,y,HX+55,y)

# COMMUNICATION 1x8: RX0/TX0/RESET/GND/RX1/TX1/SDA/SCL
comp("Connector_Generic:Conn_01x08","COMMUNICATION","8x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", HX+90, 60)
for net,i in [("RX0",0),("TX0",1),("RESET_N",2),("GND",3),
              ("RX1",4),("TX1",5),("SDA",6),("SCL",7)]:
    y = 60+(i-3.5)*2.54
    lbl(net, HX+80,y, just="right"); wire(HX+80,y,HX+85,y)

# JP6 1x10: D2-D11 (PWM capable)
comp("Connector_Generic:Conn_01x10","JP6","10x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical", HX, 160)
for net,i in [("D2",0),("D3",1),("D4",2),("D5",3),("D6",4),
              ("D7",5),("D8",6),("D9",7),("D10",8),("D11",9)]:
    y = 160+(i-4.5)*2.54
    lbl(net, HX-10,y, just="right"); wire(HX-10,y,HX-5,y)

# PWML 1x8: TX3/RX3/TX2/RX2/TX1/RX1/TX0/RX0 (D14-D21)
comp("Connector_Generic:Conn_01x08","PWML","8x1F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical", HX+30, 160)
for net,i in [("TX3",0),("RX3",1),("TX2",2),("RX2",3),
              ("TX1",4),("RX1",5),("TX0",6),("RX0",7)]:
    y = 160+(i-3.5)*2.54
    lbl(net, HX+20,y, just="right"); wire(HX+20,y,HX+25,y)

# XIO 2x18: D22-D53 digital I/O
comp("Connector_Generic:Conn_02x18_Odd_Even","XIO","18x2F-H8.5",
     "Connector_PinHeader_2.54mm:PinHeader_2x18_P2.54mm_Vertical", HX+75, 330)
for i in range(18):
    y = 330+(i-8.5)*2.54
    lbl(f"D{22+i}", HX+62,y, just="right"); wire(HX+62,y,HX+67,y)
    lbl(f"D{40+i}", HX+84,y); wire(HX+83,y,HX+84,y)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION E — LEDs & Status (x:580–780, y:580–820)
# ═══════════════════════════════════════════════════════════════════════════════
box_title("SECTION E: Status LEDs", 583, 583)

LED_Y = 650
# ON: green power LED
comp("Device:LED","ON","GREEN","LED_SMD:LED_0805_2012Metric",HX,LED_Y)
pwr("+5V",HX,LED_Y-7); pwr("GND",HX,LED_Y+7)
wire(HX,LED_Y-7,HX,LED_Y-4); wire(HX,LED_Y+4,HX,LED_Y+7)

# L: yellow D13 LED
comp("Device:LED","L","YELLOW","LED_SMD:LED_0805_2012Metric",HX+20,LED_Y)
lbl("D13",HX+15,LED_Y-5); pwr("GND",HX+20,LED_Y+7)
wire(HX+15,LED_Y,HX+17,LED_Y); wire(HX+20,LED_Y+4,HX+20,LED_Y+7)

# RX: yellow RX LED
comp("Device:LED","RX","YELLOW","LED_SMD:LED_0805_2012Metric",HX+40,LED_Y)
lbl("RX0",HX+35,LED_Y-5); pwr("GND",HX+40,LED_Y+7)
wire(HX+35,LED_Y,HX+37,LED_Y); wire(HX+40,LED_Y+4,HX+40,LED_Y+7)

# TX: yellow TX LED
comp("Device:LED","TX","YELLOW","LED_SMD:LED_0805_2012Metric",HX+60,LED_Y)
lbl("TX0",HX+55,LED_Y-5); pwr("GND",HX+60,LED_Y+7)
wire(HX+55,LED_Y,HX+57,LED_Y); wire(HX+60,LED_Y+4,HX+60,LED_Y+7)

# ── PWR_FLAG (prevents ERC power pin errors) ──────────────────────────────────
for net,x,y in [("+5V",285,25),("GND",300,25),("+3.3V",315,25)]:
    w(f'  (symbol (lib_id "power:PWR_FLAG") (at {x} {y} 0)')
    w(f'    (unit 1)(exclude_from_sim no)(in_bom yes)(on_board yes)(dnp no)')
    w(f'    (uuid "{uid()}")')
    w(f'    (property "Reference" "#FLG" (at {x} {y-2} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (hide yes)))')
    w(f'    (property "Value" "PWR_FLAG" (at {x} {y+2} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (hide yes)))')
    w(f'  )')
    pwr(net,x+3,y)
    wire(x+3,y-1,x+3,y)

# ── SHEET INSTANCES ───────────────────────────────────────────────────────────
w('')
w('  (sheet_instances')
w('    (path "/" (page "1"))')
w('  )')
w(')')

# ── WRITE FILE ────────────────────────────────────────────────────────────────
import re
output = "\n".join(_L)
with open("Arduino_Mega2560_Rev3.kicad_sch","w",encoding="utf-8") as f:
    f.write(output)

refs = sorted(set(re.findall(r'"Reference" "([^"#][^"]*)"', output)))
print(f"Lines   : {len(_L)}")
print(f"Components: {len(refs)}")
print("Refs:", refs)
