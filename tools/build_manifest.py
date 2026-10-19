#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
IGNORE={'.git','.venv','reproduced','__pycache__','.matplotlib'}
def main():
    rows=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file() or p.name=='manifest.csv' or any(x in IGNORE for x in p.relative_to(ROOT).parts):continue
        rows.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    with (ROOT/'manifest.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=['path','bytes','sha256']);writer.writeheader();writer.writerows(rows)
    print(json.dumps({'manifest':'manifest.csv','files':len(rows)}))
if __name__=='__main__':main()
