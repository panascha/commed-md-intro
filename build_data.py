#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract MD student roster + nicknames → data.json
Source: รายชื่อนักศึกษาCOMMED2569_ชื่อเล่น.xlsx
Output: data.json (gitignored, deployed alongside HTML)
"""
import json, sys
import openpyxl

SRC = "รายชื่อนักศึกษาCOMMED2569_ชื่อเล่น.xlsx"
OUT = "data.json"

# Zone names
ZONES = {
    1: "บ้านหินกอง หมู่ 4",
    2: "บ้านกระเดื่อง หมู่ 9",
    3: "บ้านเหล่า หมู่ 3",
    4: "บ้านกระพี้ หมู่ 8",
    5: "บ้านหนองสวรรค์ หมู่ 5",
    6: "บ้านหนองสุขเจริญ หมู่ 13",
    7: "บ้านแดง หมู่ 6",
    8: "บ้านบึงสวาง หมู่ 11",
    9: "บ้านใหม่สุขสันติ หมู่ 14",
}

GENDER = {1: "ชาย", 2: "หญิง"}

try:
    wb = openpyxl.load_workbook(SRC, data_only=True)
except FileNotFoundError:
    print(f"ERROR: {SRC} not found. Run from project root.", file=sys.stderr)
    sys.exit(1)

ws = wb["MD 743102"]
rows = list(ws.iter_rows(values_only=True))

# Header: row 3 (0-indexed: 3), data from row 4
# Cols: 0=ลำดับ, 1=ลำดับที่, 2=รหัส, 3=คำนำหน้า, 4=email, 5=สาขา,
#        6=เพศ, 7=เขตฝึก, 8=บ้านพัก, 9=โครงการ, 10=วิถีศึกษา, 11=ครอบครัว, 12=ชื่อเล่น
students = []
for row in rows[4:]:
    if not row or not row[2]:
        continue
    sid = str(row[2]).strip()
    if not sid:
        continue
    name_raw = str(row[3]).strip() if row[3] else ""
    nickname = str(row[12]).strip() if len(row) > 12 and row[12] else ""
    email = str(row[4]).strip() if row[4] else ""
    gender = int(row[6]) if row[6] else 0
    zone = int(row[7]) if row[7] else 0
    house = int(row[8]) if row[8] else 0
    project = int(row[9]) if row[9] else 0
    way_of_life = int(row[10]) if row[10] else 0
    family = int(row[11]) if row[11] else 0
    branch = str(row[5]).strip().upper() if row[5] else ""

    students.append({
        "id": sid,
        "name": name_raw,
        "nickname": nickname,
        "email": email,
        "gender": gender,
        "gender_th": GENDER.get(gender, ""),
        "zone": zone,
        "zone_name": ZONES.get(zone, ""),
        "house": house,
        "project": project,
        "way_of_life": way_of_life,
        "family": family,
        "branch": branch,
    })

md_only = [s for s in students if s.get("branch") == "MD"]
print(f"Total rows: {len(students)}")
print(f"MD students: {len(md_only)}")
print(f"Zones found: {sorted(set(s['zone'] for s in md_only))}")
print(f"Houses per zone:")
for z in sorted(ZONES):
    zh = [s for s in md_only if s["zone"] == z]
    print(f"  เขต {z}: {len(zh)} students, houses {sorted(set(s['house'] for s in zh))}")

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"students": md_only, "zones": ZONES}, f, ensure_ascii=False, indent=2)

sys.stdout.buffer.write(f"\nWrote {len(md_only)} MD students → {OUT}\n".encode('utf-8'))