# SPDX-License-Identifier: MIT
"""Local, typed JSON inputs and isolated output paths for report reproduction."""
from functools import lru_cache
from pathlib import Path
import csv
import json
import os

ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / 'data'
OUTPUT_ROOT = Path(os.environ.get('GREEN_COMPUTE_OUTPUT', str(ROOT / 'reproduced'))).resolve()
for protected in (DATA_ROOT, ROOT / 'src', ROOT / 'tools', ROOT / 'figures', ROOT / 'report', ROOT / 'manuscript', ROOT / 'references', ROOT / 'docs', ROOT / 'LICENSES'):
    if OUTPUT_ROOT == protected.resolve() or protected.resolve() in OUTPUT_ROOT.parents:
        raise ValueError(f'Output must be separate from published inputs: {OUTPUT_ROOT}')
if OUTPUT_ROOT == ROOT:
    raise ValueError('Use a separate output directory, not the release root.')
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


def _decode(value):
    if isinstance(value, list):
        return [_decode(v) for v in value]
    if isinstance(value, dict):
        if set(value) == {'__tuple__'}:
            return tuple(_decode(v) for v in value['__tuple__'])
        if set(value) == {'__pairs__'}:
            return {_decode(k): _decode(v) for k, v in value['__pairs__']}
        return {k: _decode(v) for k, v in value.items()}
    return value


@lru_cache(maxsize=8)
def _load(name):
    path = DATA_ROOT / 'parameters' / name
    if path.resolve().parent != (DATA_ROOT / 'parameters').resolve():
        raise ValueError('Parameter file must be inside data/parameters.')
    return _decode(json.loads(path.read_text(encoding='utf-8')))


def get_input(filename, function, group):
    # Return a fresh value: analysis functions may modify lists or dictionaries.
    import copy
    return copy.deepcopy(_load(filename)[function][group])


@lru_cache(maxsize=128)
def table_path(table_id):
    with (DATA_ROOT / 'metadata/data_catalog.csv').open(encoding='utf-8-sig', newline='') as stream:
        for row in csv.DictReader(stream):
            if row['table_id'] == table_id:
                path = (ROOT / row['path']).resolve()
                if DATA_ROOT.resolve() not in path.parents:
                    raise ValueError(f'Catalog entry escapes data directory: {table_id}')
                if not path.is_file():
                    raise FileNotFoundError(path)
                return path
    raise KeyError(f'Unknown table id: {table_id}')
