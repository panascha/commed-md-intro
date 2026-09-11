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

# Inject embedded data before </script>
data_js = f"const EMBEDDED_DATA = {json.dumps(data, ensure_ascii=False)};"
html = html.replace("</script>", data_js + "\n</script>", 1)

# Replace fetch with preference for embedded data
old_fetch = "fetch('data.json').then(r=>r.json())"
new_fetch = "(typeof EMBEDDED_DATA !== 'undefined' ? Promise.resolve(EMBEDDED_DATA) : fetch('data.json').then(r=>r.json()))"
html = html.replace(old_fetch, new_fetch)

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)

sys.stdout.buffer.write(f"Built {OUT} ({len(html):,} bytes)\n".encode('utf-8'))
