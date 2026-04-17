"""
Build hierarchical practice schematic for student collaboration.
Creates 4 section sub-sheets in the practice project.
"""
import uuid, os, shutil

BASE = r"D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Practice"

def uid(): return str(uuid.uuid4())

# Fixed UUIDs for the root schematic and 4 sections
ROOT_UUID     = "a1b2c3d4-0001-0000-0000-000000000001"
S1_UUID       = "a1b2c3d4-0001-0000-0000-000000000002"  # USB + ATmega16U2
S2_UUID       = "a1b2c3d4-0001-0000-0000-000000000003"  # ATmega2560 MCU
S3_UUID       = "a1b2c3d4-0001-0000-0000-000000000004"  # Power Supply
S4_UUID       = "a1b2c3d4-0001-0000-0000-000000000005"  # Arduino Headers

sections = [
    (S1_UUID, "Section_01_USB_ATmega16U2",  "Section 01: USB Interface & ATmega16U2"),
    (S2_UUID, "Section_02_ATmega2560_MCU",  "Section 02: ATmega2560 Main MCU"),
    (S3_UUID, "Section_03_Power_Supply",    "Section 03: Power Supply"),
    (S4_UUID, "Section_04_Arduino_Headers", "Section 04: Arduino Headers"),
]

# ── Blank sub-sheet template ──────────────────────────────────────────────────
def make_subsheet(title, comment):
    return f"""(kicad_sch
\t(version 20231120)
\t(generator "kicad_symbol_editor")
\t(generator_version "9.0")
\t(paper "A4")
\t(title_block
\t\t(title "{title}")
\t\t(date "2026-04-10")
\t\t(rev "1")
\t\t(comment 1 "Arduino Mega 2560 - Student Practice")
\t\t(comment 2 "{comment}")
\t\t(comment 3 "Use symbols from: Arduino_Mega2560_Lib")
\t)
\t(lib_symbols)
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
"""

# ── Root schematic with 4 sheet boxes ────────────────────────────────────────
def make_root():
    # Sheet box layout: 2 columns x 2 rows
    # Col1: x=20, Col2: x=130  |  Row1: y=20, Row2: y=100
    positions = [(20, 25), (130, 25), (20, 100), (130, 100)]
    box_w, box_h = 90, 55

    sheet_blocks = ""
    for i, (s_uuid, fname, title) in enumerate(sections):
        x, y = positions[i]
        sheet_ref_uuid = uid()
        sheet_blocks += f"""
\t(sheet
\t\t(at {x} {y})
\t\t(size {box_w} {box_h})
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(dnp no)
\t\t(stroke (width 0.1524) (type solid))
\t\t(fill (color 0 0 0 0.0000))
\t\t(uuid "{s_uuid}")
\t\t(property "Sheetname" "{title}"
\t\t\t(at {x} {y - 0.8} 0)
\t\t\t(effects (font (size 1.27 1.27)) (justify left bottom))
\t\t)
\t\t(property "Sheetfile" "{fname}.kicad_sch"
\t\t\t(at {x} {y + box_h + 0.8} 0)
\t\t\t(effects (font (size 1.27 1.27)) (justify left top))
\t\t)
\t\t(instances
\t\t\t(project "Arduino_Mega2560_Practice"
\t\t\t\t(path "/{ROOT_UUID}"
\t\t\t\t\t(page "{i+2}")
\t\t\t\t)
\t\t\t)
\t\t)
\t)"""

    return f"""(kicad_sch
\t(version 20231120)
\t(generator "kicad_symbol_editor")
\t(generator_version "9.0")
\t(uuid "{ROOT_UUID}")
\t(paper "A4")
\t(title_block
\t\t(title "Arduino Mega 2560 - Practice Project")
\t\t(date "2026-04-10")
\t\t(rev "1")
\t\t(company "Arduino Practice")
\t\t(comment 1 "Fork this repo, each member draws one section")
\t\t(comment 2 "Reference: MEGA2560_Rev3e_sch.pdf")
\t\t(comment 3 "Symbol library: Arduino_Mega2560_Lib")
\t)
\t(lib_symbols)
{sheet_blocks}
\t(sheet_instances
\t\t(path "/"
\t\t\t(page "1")
\t\t)
\t)
)
"""

# ── kicad_pro ─────────────────────────────────────────────────────────────────
def make_pro():
    sheets_json = ",\n    ".join(
        f'["{s_uuid}", "{fname}"]'
        for s_uuid, fname, _ in [(ROOT_UUID, "Root", "")] + [(s,f,t) for s,f,t in sections]
    )
    return f"""{{
  "meta": {{
    "filename": "Arduino_Mega2560_Practice.kicad_pro",
    "version": 1
  }},
  "schematic": {{
    "annotate_start_num": 0,
    "default_bus_thickness": 12.0,
    "default_junction_size": 0.0,
    "default_line_thickness": 6.0,
    "default_text_size": 50.0,
    "default_wire_thickness": 6.0,
    "drawing_sheet_file": "",
    "field_names": [],
    "junction_size_choice": 3,
    "label_size_ratio": 0.375,
    "pin_symbol_size": 0.0,
    "subpart_first_id": 65,
    "subpart_id_separator": 0
  }},
  "sheets": [
    ["{ROOT_UUID}", "Root"],
    {sheets_json.split(chr(10), 1)[1] if chr(10) in sheets_json else sheets_json}
  ],
  "text_variables": {{}}
}}
"""

# ── Write all files ───────────────────────────────────────────────────────────
os.makedirs(BASE, exist_ok=True)

# Root schematic
with open(os.path.join(BASE, "Arduino_Mega2560_Practice.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(make_root())
print("✓ Arduino_Mega2560_Practice.kicad_sch (root, 4 sheet boxes)")

# Sub-sheets
descriptions = {
    "Section_01_USB_ATmega16U2":  "USB-C connector, ESD protection, ferrite bead, ATmega16U2, crystal Y2, ICSP header",
    "Section_02_ATmega2560_MCU":  "ATmega2560-16AU, decoupling caps, AREF cap, crystal Y1, reset circuit, ICSP header",
    "Section_03_Power_Supply":    "DC barrel jack, NCP1117 5V LDO, LP2985 3.3V LDO, PMV48XP PMOS, LMV358, power LEDs",
    "Section_04_Arduino_Headers": "All Arduino pin headers (digital 0-53, analog A0-A15, power header, ICSP)",
}
for s_uuid, fname, title in sections:
    path = os.path.join(BASE, f"{fname}.kicad_sch")
    with open(path, "w", encoding="utf-8") as f:
        f.write(make_subsheet(title, descriptions[fname]))
    print(f"✓ {fname}.kicad_sch")

# kicad_pro
with open(os.path.join(BASE, "Arduino_Mega2560_Practice.kicad_pro"), "w", encoding="utf-8") as f:
    f.write(make_pro())
print("✓ Arduino_Mega2560_Practice.kicad_pro")

print("\nDone. Practice project restructured with 4 hierarchical sections.")
