#!/usr/bin/env python3
"""
Build Arduino Mega 2560 Practice KiCad Project
Parses 4 schematic files, extracts symbol definitions and footprint assignments,
creates a new practice project with a comprehensive pre-linked symbol library.
"""

import os
import re
import shutil
import json
import uuid

# ─── Paths ────────────────────────────────────────────────────────────────────
SRC_DIR = r"D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Rev3"
OUT_DIR = r"D:\AWORKSPACE\Github\kicad\Arduino_Mega2560_Practice"

SCH_FILES = [
    os.path.join(SRC_DIR, "Arduino Mega 2560.kicad_sch"),
    os.path.join(SRC_DIR, "ATMEGA2560-16AU.kicad_sch"),
    os.path.join(SRC_DIR, "Power.kicad_sch"),
    os.path.join(SRC_DIR, "Headers.kicad_sch"),
]

SRC_FP_DIR  = os.path.join(SRC_DIR, "Arduino Mega 2560.pretty")
OUT_FP_DIR  = os.path.join(OUT_DIR, "Arduino_Mega2560_FP.pretty")
OUT_SYM_LIB = os.path.join(OUT_DIR, "Arduino_Mega2560_Lib.kicad_sym")
OUT_PRO     = os.path.join(OUT_DIR, "Arduino_Mega2560_Practice.kicad_pro")
OUT_SCH     = os.path.join(OUT_DIR, "Arduino_Mega2560_Practice.kicad_sch")
OUT_FP_TBL  = os.path.join(OUT_DIR, "fp-lib-table")
OUT_SYM_TBL = os.path.join(OUT_DIR, "sym-lib-table")

# Old custom FP lib name → new name mapping
OLD_FP_LIB = "Arduino Mega 2560"
NEW_FP_LIB = "Arduino_Mega2560_FP"

# ─── Naming map: (lib_id, footprint_key) → symbol_name ───────────────────────
# footprint_key can be partial or full; we'll match 'in' the footprint string
NAMING_MAP = [
    # Capacitors
    ("Device:C",            "C_0603_1608Metric",            "C_SMD_0603"),
    ("Device:C",            "CAP_EEHZA1E470P",              "C_Pol_47u_THT"),
    ("Device:C_Polarized",  "",                             "C_Pol"),
    # Resistors
    ("Device:R",            "R_0603_1608Metric",            "R_SMD_0603"),
    ("Device:R_Pack04_Split","R_Array_Convex_4x0612",       "RArray_4x0612"),
    ("Device:R_Pack04_Split","",                            "RArray_4x"),
    ("Device:Varistor",     "R_0603_1608Metric",            "Varistor_0603"),
    # LED / Diode
    ("Device:LED",          "LED_0805_2012Metric",          "LED_0805"),
    ("Device:D",            "D_1206_3216Metric",            "D_1206"),
    ("Device:D",            "D_SMB",                        "D_SMB"),
    # FerriteBead / Fuse
    ("Device:FerriteBead",  "L_0805_2012Metric",            "FerriteBead_0805"),
    ("Device:Fuse",         "1812",                         "Fuse_1812"),
    ("Device:Fuse",         "",                             "Fuse"),
    # Crystals / Resonators
    ("Device:Crystal",      "Crystal_HC49-4H_Vertical",     "Crystal_HC49"),
    ("Device:Crystal",      "",                             "Crystal"),
    ("Device:Crystal_GND2", "",                             "Resonator_3Pin"),
    # Jumper / Mechanical
    ("Jumper:SolderJumper_2_Open", "",                      "SolderJumper_2"),
    ("Mechanical:Fiducial", "",                             "Fiducial_1mm"),
    # USB Connector
    ("Connector:USB_C_Receptacle_USB2.0_16P", "",           "USB_C_16P"),
    # Generic Connectors
    ("Connector_Generic:Conn_02x03_Odd_Even", "PinHeader",  "Header_2x03"),
    ("Connector_Generic:Conn_02x03_Odd_Even", "",           "Header_2x03"),
    ("Connector_Generic:Conn_02x02_Odd_Even", "",           "Header_2x02"),
    # PinSocket / PinHeader
    ("Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical", "", "PinSocket_1x08"),
    ("Connector_PinSocket_2.54mm:PinSocket_1x10_P2.54mm_Vertical", "", "PinSocket_1x10"),
    ("Connector_PinHeader_2.54mm:PinHeader_2x03_P2.54mm_Vertical", "", "PinHeader_2x03"),
    # Barrel Jack
    ("Connector_BarrelJack:Barrel_Jack_Switch", "",         "BarrelJack"),
    # Arduino custom symbols
    ("Arduino Mega 2560:ATMEGA16U2-MU",  "",               "ATmega16U2_MU"),
    ("Arduino Mega 2560:ATMEGA2560-16AU","",               "ATmega2560_16AU"),
    ("Arduino Mega 2560:LMV358IDGKR",   "",               "LMV358"),
    ("Arduino Mega 2560:TS06-667-30-BK-100-G-SMT-TR", "", "SW_Reset"),
    ("Arduino Mega 2560:PPTC182LFBN-RC","",               "Arduino_Header_2x18"),
    ("Arduino Mega 2560:CONN_M20-9980245_HRW", "",         "ICSP_3x2_Header"),
    # Transistor / FET
    ("Transistor_FET:Q_PMOS_GSD",       "",               "PMOS_PMV48XP"),
    # Voltage Regulators
    ("power:+5V",    "",               "PWR_5V"),
    ("power:+3.3V",  "",               "PWR_3V3"),
    ("power:GND",    "",               "PWR_GND"),
    ("power:+VIN",   "",               "PWR_VIN"),
    ("power:+VUSB",  "",               "PWR_VUSB"),
    ("power:+AREF",  "",               "PWR_AREF"),
    ("power:+AVCC",  "",               "PWR_AVCC"),
    ("power:+IOREF", "",               "PWR_IOREF"),
    # Regulators (these will be auto-detected by lib_id pattern match)
    ("Regulator_Linear:NCP1117",        "",               "LDO_NCP1117_5V"),
    ("Regulator_Linear:LP2985",         "",               "LDO_LP2985_3V3"),
]

# ─── S-Expression Parser ──────────────────────────────────────────────────────

def extract_top_level_symbols_in_section(text, section_name):
    """
    Find a top-level section like (lib_symbols ...) and return
    a list of (name, full_text) for each (symbol ...) inside it.
    """
    # Find the section
    pattern = r'\(' + re.escape(section_name) + r'\s'
    m = re.search(pattern, text)
    if not m:
        print(f"  [WARN] section '{section_name}' not found")
        return []

    start = m.start()
    # Walk forward to find matching close paren
    depth = 0
    i = start
    while i < len(text):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                section_text = text[start:i+1]
                break
        i += 1
    else:
        print(f"  [WARN] section '{section_name}' not properly closed")
        return []

    # Now extract each (symbol ...) inside the section
    symbols = []
    j = len(f'({section_name}')  # skip the opening
    inner = section_text[j:-1]   # strip outer parens

    k = 0
    while k < len(inner):
        if inner[k] == '(' :
            # Check if this is (symbol ...
            rest = inner[k:]
            sym_m = re.match(r'\(symbol\s+"([^"]+)"', rest)
            if sym_m:
                sym_name = sym_m.group(1)
                # extract balanced block
                d = 0
                end_k = k
                for ci, ch in enumerate(rest):
                    if ch == '(':
                        d += 1
                    elif ch == ')':
                        d -= 1
                        if d == 0:
                            end_k = k + ci
                            break
                sym_text = inner[k:end_k+1]
                symbols.append((sym_name, sym_text))
                k = end_k + 1
                continue
        k += 1

    return symbols


def extract_placed_components(text):
    """
    Extract all placed (symbol ...) instances from a schematic,
    returning list of dicts with lib_id, footprint, reference, value.
    Placed symbols appear AFTER the lib_symbols section.
    """
    # Skip the lib_symbols section first
    ls_m = re.search(r'\(lib_symbols\s', text)
    if ls_m:
        # find end of lib_symbols
        depth = 0
        i = ls_m.start()
        while i < len(text):
            if text[i] == '(':
                depth += 1
            elif text[i] == ')':
                depth -= 1
                if depth == 0:
                    search_start = i + 1
                    break
            i += 1
        else:
            search_start = 0
    else:
        search_start = 0

    components = []
    remaining = text[search_start:]

    # Find all placed (symbol (lib_id "...") ...) blocks
    k = 0
    while k < len(remaining):
        if remaining[k] == '(':
            rest = remaining[k:]
            # Match a top-level placed symbol
            sym_m = re.match(r'\(symbol\s*\n?\s*\(lib_id\s+"([^"]+)"', rest)
            if sym_m:
                lib_id = sym_m.group(1)
                # Extract full block
                d = 0
                end_k = k
                for ci, ch in enumerate(rest):
                    if ch == '(':
                        d += 1
                    elif ch == ')':
                        d -= 1
                        if d == 0:
                            end_k = k + ci
                            break
                sym_block = rest[:end_k+1]

                # Extract footprint property
                fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', sym_block)
                footprint = fp_m.group(1) if fp_m else ""

                # Extract reference
                ref_m = re.search(r'\(property\s+"Reference"\s+"([^"]*)"', sym_block)
                reference = ref_m.group(1) if ref_m else ""

                # Extract value
                val_m = re.search(r'\(property\s+"Value"\s+"([^"]*)"', sym_block)
                value = val_m.group(1) if val_m else ""

                components.append({
                    'lib_id': lib_id,
                    'footprint': footprint,
                    'reference': reference,
                    'value': value,
                })
                k = end_k + 1
                continue
        k += 1

    return components


def get_symbol_name(lib_id, footprint):
    """
    Generate a descriptive symbol name based on naming map.
    Falls back to sanitizing the lib_id if not found.
    """
    # Try exact lib_id + footprint substring match
    for map_lib_id, fp_key, name in NAMING_MAP:
        if lib_id == map_lib_id:
            if fp_key == "" or fp_key in footprint:
                return name

    # Auto-generate: take last part of lib_id, sanitize
    parts = lib_id.split(":")
    base = parts[-1] if len(parts) > 1 else parts[0]
    # Remove spaces, special chars
    base = re.sub(r'[^a-zA-Z0-9_]', '_', base)
    return base


def update_footprint_in_symbol(sym_text, new_footprint, original_name=None):
    """
    Replace the Footprint property value in a symbol definition.
    Also rename old FP lib references ONLY in property values (not symbol names).
    original_name: if provided, protect the symbol name from replacement.
    """
    # We need to rename "Arduino Mega 2560:xxx" → "Arduino_Mega2560_FP:xxx"
    # BUT only in property values, not in (symbol "...") name lines.
    # Strategy: replace in footprint property specifically, then in all other
    # quoted strings that are not symbol-name declarations.

    # First, update the Footprint property value
    if new_footprint:
        new_fp = new_footprint.replace(f'{OLD_FP_LIB}:', f'{NEW_FP_LIB}:')
    else:
        new_fp = None

    # Process line by line to avoid touching (symbol "...") declarations
    lines = sym_text.split('\n')
    result_lines = []
    for line in lines:
        # Skip lines that are symbol name declarations (protect them from replacement)
        # These look like: (symbol "Arduino Mega 2560:NAME" or (symbol "NAME_x_y"
        sym_decl = re.match(r'^(\s*\(symbol\s+")', line)
        if sym_decl:
            result_lines.append(line)
            continue

        # Replace footprint property value
        if new_fp and '(property "Footprint"' in line:
            line = re.sub(
                r'\(property\s+"Footprint"\s+"[^"]*"',
                f'(property "Footprint" "{new_fp}"',
                line
            )
        elif '(property "Footprint"' in line:
            # Still need to rename FP lib refs in footprint value
            line = re.sub(
                r'"' + re.escape(OLD_FP_LIB) + r':',
                f'"{NEW_FP_LIB}:',
                line
            )

        # In other property lines that reference the old FP lib name in values
        # (e.g. custom footprint references in non-footprint properties)
        # Actually only update footprint-like references in property values
        result_lines.append(line)

    return '\n'.join(result_lines)


def rename_symbol_in_def(sym_text, original_name, new_name):
    """
    Rename the symbol name in its definition text.
    e.g. (symbol "Device:C" ...) → (symbol "C_SMD_0603" ...)
    Also rename subsymbol entries like (symbol "Device:C_0_1" ...)

    For Arduino Mega 2560 lib symbols, the original_name has spaces/colons
    which can't appear in sub-symbol names — sub-symbols use just the local part.
    """
    escaped = re.escape(original_name)

    # Determine the local part of the original name (after the colon, if any)
    if ':' in original_name:
        local_part = original_name.split(':', 1)[1]
    else:
        local_part = original_name
    escaped_local = re.escape(local_part)

    # Replace main symbol name (the outer declaration)
    sym_text = re.sub(
        r'\(symbol\s+"' + escaped + r'"',
        f'(symbol "{new_name}"',
        sym_text,
        count=1
    )
    # Replace sub-symbol names: could be "OriginalName_0_1" or "LocalPart_0_1"
    # First try full name with colon
    sym_text = re.sub(
        r'\(symbol\s+"' + escaped + r'(_\d+_\d+)"',
        f'(symbol "{new_name}\\1"',
        sym_text
    )
    # Then try local part only (handles Arduino Mega 2560:XXX → sub "XXX_0_1")
    sym_text = re.sub(
        r'\(symbol\s+"' + escaped_local + r'(_\d+_\d+)"',
        f'(symbol "{new_name}\\1"',
        sym_text
    )
    return sym_text


# ─── Main Processing ──────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Arduino Mega 2560 Practice Project Builder")
    print("=" * 60)

    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(OUT_FP_DIR, exist_ok=True)

    # Step 1: Copy footprint files
    print("\n[1] Copying footprint files...")
    fp_files = [f for f in os.listdir(SRC_FP_DIR) if f.endswith('.kicad_mod')]
    for fp_file in fp_files:
        src = os.path.join(SRC_FP_DIR, fp_file)
        dst = os.path.join(OUT_FP_DIR, fp_file)
        shutil.copy2(src, dst)
        print(f"    Copied: {fp_file}")

    # Step 2: Parse all schematics
    print("\n[2] Parsing schematic files...")

    # Map: lib_id → symbol_definition_text (from lib_symbols)
    all_sym_defs = {}
    # Map: lib_id → set of footprints seen in placed instances
    lib_id_footprints = {}

    for sch_path in SCH_FILES:
        if not os.path.exists(sch_path):
            print(f"  [SKIP] Not found: {sch_path}")
            continue

        fname = os.path.basename(sch_path)
        print(f"\n  Processing: {fname}")

        with open(sch_path, 'r', encoding='utf-8') as f:
            text = f.read()

        # Extract lib_symbols
        sym_defs = extract_top_level_symbols_in_section(text, "lib_symbols")
        print(f"    Found {len(sym_defs)} symbol definitions in lib_symbols")

        for sym_name, sym_text in sym_defs:
            if sym_name not in all_sym_defs:
                all_sym_defs[sym_name] = sym_text
                # print(f"      Stored def: {sym_name}")

        # Extract placed components
        components = extract_placed_components(text)
        print(f"    Found {len(components)} placed component instances")

        for comp in components:
            lid = comp['lib_id']
            fp  = comp['footprint']
            if lid not in lib_id_footprints:
                lib_id_footprints[lid] = set()
            if fp:
                lib_id_footprints[lid].add(fp)

    print(f"\n  Total unique symbol definitions: {len(all_sym_defs)}")
    print(f"  Total unique lib_ids with placed instances: {len(lib_id_footprints)}")

    # Step 3: Build (lib_id, footprint) → symbol_name mapping
    print("\n[3] Building symbol entries...")

    # Track all (lib_id, footprint) pairs from placed instances
    entries = []  # list of (lib_id, footprint, sym_name)
    used_names = {}  # name → count for dedup

    # Collect all unique (lib_id, footprint) combinations
    pairs = []
    for lib_id, fps in sorted(lib_id_footprints.items()):
        if fps:
            for fp in sorted(fps):
                pairs.append((lib_id, fp))
        else:
            pairs.append((lib_id, ""))

    # Also add any sym_defs that have no placed instances (from lib_symbols only)
    # but only if they're from the custom Arduino lib
    for sym_name in sorted(all_sym_defs.keys()):
        lib_id = sym_name  # In lib_symbols, the key IS the lib_id
        if lib_id not in lib_id_footprints:
            # Try to get footprint from the definition itself
            sym_text = all_sym_defs[lib_id]
            fp_m = re.search(r'\(property\s+"Footprint"\s+"([^"]*)"', sym_text)
            fp = fp_m.group(1) if fp_m else ""
            pairs.append((lib_id, fp))

    # Deduplicate pairs
    seen_pairs = set()
    unique_pairs = []
    for p in pairs:
        if p not in seen_pairs:
            seen_pairs.add(p)
            unique_pairs.append(p)

    print(f"  Total (lib_id, footprint) pairs: {len(unique_pairs)}")

    # Generate names
    name_to_pairs = {}  # name → list of (lib_id, fp)
    pair_to_name  = {}  # (lib_id, fp) → name

    for lib_id, fp in unique_pairs:
        name = get_symbol_name(lib_id, fp)
        if name not in name_to_pairs:
            name_to_pairs[name] = []
        name_to_pairs[name].append((lib_id, fp))

    # Resolve name conflicts: if multiple pairs → same name, suffix with index
    for name, pairs_list in name_to_pairs.items():
        if len(pairs_list) == 1:
            pair_to_name[pairs_list[0]] = name
        else:
            for idx, pair in enumerate(pairs_list):
                pair_to_name[pair] = f"{name}_{idx+1}"

    # Step 4: Write symbol library
    print("\n[4] Writing symbol library...")

    sym_lib_lines = []
    sym_lib_lines.append('(kicad_symbol_lib')
    sym_lib_lines.append('  (version 20231120)')
    sym_lib_lines.append('  (generator "kicad_symbol_editor")')
    sym_lib_lines.append('  (generator_version "9.0")')

    created_count = 0
    skipped_count = 0
    created_symbols = []

    for (lib_id, fp), sym_name in sorted(pair_to_name.items(), key=lambda x: x[1]):
        # Find the symbol definition
        sym_def = all_sym_defs.get(lib_id)
        if sym_def is None:
            print(f"  [SKIP] No definition found for lib_id: {lib_id}")
            skipped_count += 1
            continue

        # Rename symbol FIRST (before any string replacement that might touch symbol names)
        updated = rename_symbol_in_def(sym_def, lib_id, sym_name)

        # Update footprint (now safe — symbol name is already the new clean name)
        updated = update_footprint_in_symbol(updated, fp, original_name=sym_name)

        # Indent for library (add 2 spaces)
        indented = '\n'.join('  ' + line for line in updated.split('\n'))
        sym_lib_lines.append(indented)

        created_count += 1
        created_symbols.append((sym_name, lib_id, fp))
        print(f"    + {sym_name:40s} ← {lib_id}  [{fp[:50] if fp else '(no fp)'}]")

    sym_lib_lines.append(')')

    with open(OUT_SYM_LIB, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sym_lib_lines))
    print(f"\n  Wrote {created_count} symbols to: {OUT_SYM_LIB}")

    # Step 5: Write blank schematic
    print("\n[5] Writing blank schematic...")
    sch_uuid = str(uuid.uuid4())
    sch_content = f"""(kicad_sch
  (version 20231120)
  (generator "eeschema")
  (generator_version "9.0")
  (uuid "{sch_uuid}")
  (paper "A4")
  (title_block
    (title "Arduino Mega 2560 - Practice")
    (date "2026-04-10")
    (rev "1")
    (comment 1 "Draw the schematic following the PDF reference")
    (comment 2 "Use symbols from: Arduino_Mega2560_Lib")
  )
  (lib_symbols
  )
  (sheet_instances
    (path "/"
      (page "1")
    )
  )
)
"""
    with open(OUT_SCH, 'w', encoding='utf-8') as f:
        f.write(sch_content)
    print(f"  Wrote: {OUT_SCH}")

    # Step 6: Write project file
    print("\n[6] Writing project file...")
    pro_data = {
        "meta": {
            "filename": "Arduino_Mega2560_Practice.kicad_pro",
            "version": 1
        },
        "board": {
            "design_settings": {},
            "layer_presets": [],
            "viewports": []
        },
        "boards": [],
        "cvpcb": {
            "equivalence_files": []
        },
        "erc": {
            "erc_exclusions": [],
            "meta": {"version": 0},
            "pin_map": [],
            "rule_severities": {}
        },
        "libraries": {
            "pinned_footprint_libs": [],
            "pinned_symbol_libs": []
        },
        "net_settings": {
            "classes": [
                {
                    "bus_width": 12,
                    "clearance": 0.2,
                    "diff_pair_gap": 0.25,
                    "diff_pair_via_gap": 0.25,
                    "diff_pair_width": 0.2,
                    "line_style": 0,
                    "microvia_diameter": 0.3,
                    "microvia_drill": 0.1,
                    "name": "Default",
                    "pcb_color": "rgba(0, 0, 0, 0.000)",
                    "schematic_color": "rgba(0, 0, 0, 0.000)",
                    "track_width": 0.25,
                    "via_diameter": 0.8,
                    "via_drill": 0.4,
                    "wire_width": 6,
                    "bus_width": 12
                }
            ],
            "meta": {"version": 3},
            "net_colors": {}
        },
        "pcbnew": {
            "last_paths": {
                "gencad": "",
                "idf": "",
                "netlist": "",
                "specctra_dsn": "",
                "step": "",
                "vrml": ""
            },
            "page_layout_descr_file": ""
        },
        "schematic": {
            "annotate_start_num": 0,
            "drawing": {
                "dashed_lines_dash_length_ratio": 12.0,
                "dashed_lines_gap_length_ratio": 3.0,
                "default_line_thickness": 6.0,
                "default_text_size": 50.0,
                "field_names": [],
                "intersheets_ref_own_page": False,
                "intersheets_ref_prefix": "",
                "intersheets_ref_short": False,
                "intersheets_ref_show": False,
                "intersheets_ref_suffix": "",
                "junction_size_choice": 3,
                "label_size_ratio": 0.375,
                "pin_symbol_size": 0.0,
                "text_offset_ratio": 0.15
            },
            "legacy_lib_dir": "",
            "legacy_lib_list": [],
            "meta": {"version": 1},
            "net_format_name": "",
            "page_layout_descr_file": "",
            "plot_directory": "",
            "spice_adjust_passive_values": False,
            "spice_current_sheet_as_root": False,
            "subpart_first_id": 65,
            "subpart_id_separator": 0
        },
        "sheets": [
            [sch_uuid, ""]
        ],
        "text_variables": {}
    }

    with open(OUT_PRO, 'w', encoding='utf-8') as f:
        json.dump(pro_data, f, indent=2)
    print(f"  Wrote: {OUT_PRO}")

    # Step 7: Write library tables
    print("\n[7] Writing library tables...")

    fp_lib_table = """(fp_lib_table
  (version 7)
  (lib (name "Arduino_Mega2560_FP")(type "KiCad")(uri "${KIPRJMOD}/Arduino_Mega2560_FP.pretty")(options "")(descr "Arduino Mega 2560 custom footprints"))
)
"""
    with open(OUT_FP_TBL, 'w', encoding='utf-8') as f:
        f.write(fp_lib_table)
    print(f"  Wrote: {OUT_FP_TBL}")

    sym_lib_table = """(sym_lib_table
  (version 7)
  (lib (name "Arduino_Mega2560_Lib")(type "KiCad")(uri "${KIPRJMOD}/Arduino_Mega2560_Lib.kicad_sym")(options "")(descr "Arduino Mega 2560 all components with footprints"))
)
"""
    with open(OUT_SYM_TBL, 'w', encoding='utf-8') as f:
        f.write(sym_lib_table)
    print(f"  Wrote: {OUT_SYM_TBL}")

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Symbols created:   {created_count}")
    print(f"  Symbols skipped:   {skipped_count}")
    print(f"  Footprints copied: {len(fp_files)}")
    print(f"\n  Output directory: {OUT_DIR}")
    print(f"\n  Files created:")
    for f in [OUT_PRO, OUT_SCH, OUT_SYM_LIB, OUT_FP_TBL, OUT_SYM_TBL]:
        size = os.path.getsize(f)
        print(f"    {os.path.basename(f):50s} {size:>8} bytes")
    print(f"\n  All lib_ids found in placed instances:")
    for lib_id in sorted(lib_id_footprints.keys()):
        fps = lib_id_footprints[lib_id]
        print(f"    {lib_id}")
        for fp in sorted(fps):
            print(f"      → {fp}")
    print("\nDone!")


if __name__ == "__main__":
    main()
