#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproduce the frozen report models and/or figure rendering from local data."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--models', action='store_true', help='Recalculate 17 reported model tables.')
    parser.add_argument('--figures', action='store_true', help='Render the supplied report figures.')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reproduced')
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if output == ROOT or any((ROOT / p).resolve() == output or (ROOT / p).resolve() in output.parents
                             for p in ['data', 'src', 'tools', 'report', 'manuscript', 'figures', 'references', 'docs', 'LICENSES']):
        parser.error('Choose an output directory separate from published files.')
    output.mkdir(parents=True, exist_ok=True)
    run_models = args.models or not args.figures
    scripts = []
    if run_models:
        scripts.extend(['models_engineering.py', 'models_analytics.py'])
    if args.figures:
        scripts.append('render_figures.py')
    env = os.environ.copy()
    env['GREEN_COMPUTE_OUTPUT'] = str(output)
    env['MPLCONFIGDIR'] = str(output / '.matplotlib')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    runs = []
    print(json.dumps({'model_provenance': 'data/metadata/model_provenance.csv', 'output_dir': str(output), 'models': run_models, 'figures': args.figures}), flush=True)
    for script in scripts:
        start = time.monotonic()
        result = subprocess.run([sys.executable, str(ROOT / 'src' / script)], cwd=ROOT,
                                env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        (output / f'{Path(script).stem}.log').write_text(result.stdout, encoding='utf-8')
        runs.append({'script': script, 'returncode': result.returncode,
                     'elapsed_seconds': round(time.monotonic() - start, 2)})
        print(f'{script}: exit={result.returncode}, elapsed={runs[-1]["elapsed_seconds"]}s', flush=True)
        if result.returncode:
            print(result.stdout[-6000:], file=sys.stderr)
            break
    (output / 'run_status.json').write_text(json.dumps({'runs': runs, 'numerical_execution_only': True}, indent=2))
    return 0 if all(r['returncode'] == 0 for r in runs) else 1


if __name__ == '__main__':
    raise SystemExit(main())
