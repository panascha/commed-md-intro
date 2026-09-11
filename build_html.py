#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build deployable HTML by embedding data.json into intro-commed-md.html
Output: index.html (single-file, no external dependencies)
"""
import json
import sys

SRC_HTML = "intro-commed-md.html"
SRC_JSON = "data.json"
OUT = "index.html"

with open(SRC_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

with open(SRC_HTML, "r", encoding="utf-8") as f:
    html = f.read()

# Inject embedded data at the TOP of the inline script (before any code that
# references it — a const declared after use hits the TDZ and kills the script).
data_js = f"const EMBEDDED_DATA = {json.dumps(data, ensure_ascii=False)};"
script_open = "<script>\n"
assert script_open in html, "inline script tag not found"
html = html.replace(script_open, script_open + data_js + "\n", 1)

# Deploy build has no data.json alongside — always use embedded data.
old_fetch = "fetch('data.json').then(r=>r.json())"
assert old_fetch in html, "fetch call not found"
html = html.replace(old_fetch, "Promise.resolve(EMBEDDED_DATA)")

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

sys.stdout.buffer.write(f"Built {OUT} ({len(html):,} bytes)\n".encode('utf-8'))
