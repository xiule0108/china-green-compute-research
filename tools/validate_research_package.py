#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
from collections import Counter
import ast,csv,hashlib,json,re,urllib.parse

ROOT=Path(__file__).resolve().parents[1]
IGNORE={'.git','.venv','reproduced','__pycache__','.matplotlib'}
def read_csv(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:return list(csv.DictReader(stream))
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value):
    if isinstance(value,dict):
        if set(value)=={'__tuple__'}:return canonical(value['__tuple__'])
        return {k:canonical(v) for k,v in value.items()}
    return [canonical(v) for v in value] if isinstance(value,list) else value
def get_value(value,path):
    if isinstance(value,dict) and path in value:return value[path]
    head,sep,tail=path.partition('/')
    child=value[int(head)] if isinstance(value,list) else value[head]
    return get_value(child,tail) if sep else child
def leaves(value,prefix=''):
    if isinstance(value,(dict,list)):
        pairs=enumerate(value) if isinstance(value,list) else value.items()
        return {p:v for k,y in pairs for p,v in leaves(y,f'{prefix}/{k}' if prefix else str(k)).items()}
    return {prefix:value}

def main():
    errors=[];counts={}
    def err(code,path,detail=''):errors.append({'code':code,'path':str(path),'detail':str(detail)})
    def target(rel):
        path=(ROOT/rel).resolve()
        if ROOT not in path.parents or not path.is_file():err('missing_or_external_path',rel);return None
        return path
    files=[p for p in sorted(ROOT.rglob('*')) if p.is_file() and not any(x in IGNORE for x in p.relative_to(ROOT).parts)]
    for rel in ['README.md','README.zh-CN.md','CITATION.cff','LICENSE','requirements.txt','LICENSES/LICENSE-SCOPE.md']:target(rel)
    for p in files:
        rel=p.relative_to(ROOT)
        if p.is_symlink():err('symlink',rel)
        if p.name=='.DS_Store' or p.suffix.lower() in {'.doc','.docx','.pdf','.zip','.xlsx','.log'}:err('unexpected_file_type',rel)
        if any(term in p.name.lower() for term in ['antigravity','internal_audit','validation_summary','reproduction_comparison','cell_differences','issue_register','提示词','任务书','复核总表','验收报告']):err('internal_artifact',rel)
        if p.suffix=='.csv':
            try:
                with p.open(encoding='utf-8-sig',newline='') as stream:
                    rows=csv.reader(stream,strict=True);header=next(rows,[])
                    if not header:err('empty_csv',rel)
                    for row_number,row in enumerate(rows,2):
                        if row and len(row)!=len(header):err('csv_row_width',rel,row_number)
            except (csv.Error,UnicodeError) as e:err('csv_format',rel,e)
        if p.suffix in {'.py','.json'}:
            try:
                if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
                else:json.loads(p.read_text(encoding='utf-8'))
            except Exception as e:err('syntax',rel,e)
        if p.suffix in {'.md','.py','.json','.csv','.cff','.txt','.yml','.yaml'}:
            text=p.read_text(encoding='utf-8-sig')
            if re.search(r'/(?:Users|home)/[A-Za-z0-9._-]+/|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|ghp_[A-Za-z0-9]{30,}',text):err('private_path_or_secret',rel)
            if p.suffix=='.md' and re.search(r'\[\[CHART_[A-Z0-9_]+\]\]|\bTODO\b|\bTBD\b',text):err('unresolved_placeholder',rel)
    catalog=read_csv(ROOT/'data/metadata/data_catalog.csv');refs=read_csv(ROOT/'references/references.csv')
    models=read_csv(ROOT/'data/metadata/model_provenance.csv');figures=read_csv(ROOT/'data/metadata/figure_catalog.csv')
    ref_ids={r['id'] for r in refs}
    counts.update({'catalogued_tables':len(catalog),'model_records':len(models),'figure_pairs':len(figures),'source_records':len(refs)})
    if len(catalog)!=76 or len({r['table_id'] for r in catalog})!=76:err('catalog_coverage','data/metadata/data_catalog.csv')
    if len(models)!=17 or {r['model_id'] for r in models}!={r['table_id'] for r in catalog if not r['table_id'].startswith('TBL-')}:err('model_coverage','data/metadata/model_provenance.csv')
    for r in catalog:
        p=target(r['path'])
        if p and len(read_csv(p))!=int(r['rows']):err('table_row_count',r['path'])
    functions={}
    for rel in ['src/models_engineering.py','src/models_analytics.py','src/render_figures.py']:
        functions[rel]={n.name:n for n in ast.parse((ROOT/rel).read_text()).body if isinstance(n,ast.FunctionDef)}
    for r in models:
        if r['function'] not in functions.get(r['script'],{}):err('missing_model_function',r['script'],r['function'])
        for rel in r['input_files'].split(';'):target(rel)
        if set(re.findall(r'C\d{2}-S\d{3}',r['source_ids']))-ref_ids:err('unknown_model_sources',r['model_id'])
    if len(figures)!=56:err('figure_coverage','data/metadata/figure_catalog.csv')
    for r in figures:
        target(r['png']);target(r['svg'])
        fn=functions['src/render_figures.py'].get(r['function'])
        if fn is None:err('missing_render_function',r['figure_id'])
        elif int(r['line'])!=fn.lineno:err('render_function_line',r['figure_id'])
        if r['parameter_file']:target(r['parameter_file'])
    parameters={str(p.relative_to(ROOT)):json.loads(p.read_text()) for p in (ROOT/'data/parameters').glob('*.json')}
    groups=read_csv(ROOT/'data/metadata/parameter_groups.csv');inputs=read_csv(ROOT/'data/metadata/model_input_sources.csv')
    expected_groups={(pf,fn,g) for pf,data in parameters.items() for fn,values in data.items() for g in values}
    listed_groups={(r['parameter_file'],r['function'],r['parameter_group']) for r in groups}
    if expected_groups!=listed_groups or len(groups)!=len(listed_groups):err('parameter_group_coverage','data/metadata/parameter_groups.csv')
    for r in groups:
        try:value=parameters[r['parameter_file']][r['function']][r['parameter_group']]
        except (KeyError,TypeError):err('parameter_group_path',r['parameter_file'],r['parameter_group']);continue
        if value!=json.loads(r['value_json']):err('parameter_group_value',r['parameter_file'],r['parameter_group'])
    for r in inputs:
        try:value=get_value(canonical(parameters[r['parameter_file']][r['function']]),r['value_path'])
        except (KeyError,IndexError,TypeError,ValueError):err('parameter_leaf_path',r['parameter_file'],r['value_path']);continue
        if value!=json.loads(r['value_json']):err('parameter_leaf_value',r['parameter_file'],r['value_path'])
    wanted={(pf,fn,p) for pf,data in parameters.items() if pf!='data/parameters/figure_inputs.json' for fn,val in data.items() for p in leaves(canonical(val))}
    listed={(r['parameter_file'],r['function'],r['value_path']) for r in inputs}
    if wanted!=listed or len(inputs)!=len(listed):err('parameter_leaf_coverage','data/metadata/model_input_sources.csv',{'missing':sorted(wanted-listed),'extra':sorted(listed-wanted)})
    counts.update({'parameter_groups':len(groups),'model_parameter_leaves':len(inputs)})
    constants=read_csv(ROOT/'data/metadata/code_constants.csv');expected=[]
    for rel,funcs in functions.items():
        for fn in funcs.values():
            for n in ast.walk(fn):
                if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)) and not isinstance(n.value,bool):expected.append((rel,fn.name,n.lineno,n.col_offset,n.value))
    actual=[(r['script'],r['function'],int(r['line']),int(r['column']),float(r['value'])) for r in constants]
    if Counter(actual)!=Counter(expected):err('code_constants_ast','data/metadata/code_constants.csv')
    counts['code_constants']=len(constants)
    mapping=read_csv(ROOT/'data/metadata/exhibit_code_map.csv');counts['report_exhibits']=len(mapping)
    if len(mapping)!=98 or len({r['exhibit_id'] for r in mapping})!=98:err('exhibit_coverage','data/metadata/exhibit_code_map.csv')
    for r in mapping:
        target(r['manuscript_path'])
        for k in ['script','figure_png','figure_svg']:
            if r[k]:target(r[k])
        for rel in r['published_data_files'].split(';'):
            if rel:target(rel)
    tables=json.loads((ROOT/'data/metadata/report_table_registry.json').read_text());counts['report_table_csvs']=len(tables)
    if len(tables)!=43:err('report_table_coverage','data/metadata/report_table_registry.json')
    for r in tables:
        p=target(r['table_csv'])
        if p and len(read_csv(p))!=r['rows']:err('report_snapshot_rows',r['table_csv'])
    bibliography=read_csv(ROOT/'data/metadata/report_references.csv');counts['formal_references']=len(bibliography)
    if {int(r['reference_number']) for r in bibliography}!=set(range(1,127)):err('formal_reference_coverage','data/metadata/report_references.csv')
    for n in range(1,13):target(f'manuscript/zh-CN/chapter-{n:02}.md')
    language_files={lang:{p.name for p in (ROOT/'docs'/lang).glob('*.md')} for lang in ['en','zh-CN']}
    for lang,names in language_files.items():
        counts[f'docs_{lang}']=len(names)
        if not names:err('missing_language_docs',f'docs/{lang}')
    if language_files['en']!=language_files['zh-CN']:err('bilingual_doc_pairs','docs')
    anchor_cache={}
    def anchors(p):
        if p not in anchor_cache:
            txt=p.read_text();explicit=re.findall(r'<a\s+[^>]*(?:id|name)=[\"\x27]([^\"\x27]+)',txt,re.I);known=set(explicit);duplicates=Counter()
            for anchor,n in Counter(explicit).items():
                if n>1:err('duplicate_explicit_anchor',p.relative_to(ROOT),anchor)
            for header in re.findall(r'^#{1,6}\s+(.+)$',txt,re.M):
                h=re.sub(r'[`*_~]','',header).strip().lower();h=re.sub(r'[^\w\s-]','',h);h=re.sub(r'\s','-',h)
                known.add(h if not duplicates[h] else f'{h}-{duplicates[h]}');duplicates[h]+=1
            anchor_cache[p]=known
        return anchor_cache[p]
    for r in mapping:
        p=ROOT/r['manuscript_path']
        if p.is_file() and r['manuscript_anchor'].lstrip('#') not in anchors(p):err('exhibit_anchor_missing',r['manuscript_path'],r['manuscript_anchor'].lstrip('#'))
    for p in [p for p in files if p.suffix=='.md']:
        text=re.sub(r'^```[^\n]*\n.*?^```\s*$', '',p.read_text(),flags=re.M|re.S)
        for m in re.finditer(r'!?\[(?:[^\[\]\n]|\[[^\]\n]*\])*\]\(([^)\n]+)\)',text):
            href=m[1].strip().strip('<>')
            if href.startswith(('http:','https:','mailto:','data:')):continue
            path,_,fragment=href.partition('#');destination=(p.parent/urllib.parse.unquote(path)).resolve() if path else p.resolve()
            if destination!=ROOT and ROOT not in destination.parents:err('markdown_external_local_link',p.relative_to(ROOT),href)
            elif not destination.exists():err('markdown_missing_link',p.relative_to(ROOT),href)
            elif fragment and destination.suffix=='.md' and urllib.parse.unquote(fragment) not in anchors(destination):err('markdown_missing_anchor',p.relative_to(ROOT),href)
    manifest_path=ROOT/'manifest.csv'
    if not manifest_path.is_file():err('missing_manifest','manifest.csv')
    else:
        manifest=read_csv(manifest_path);listed={r['path'] for r in manifest};actual={str(p.relative_to(ROOT)) for p in files if p!=manifest_path}
        if listed!=actual:err('manifest_file_set','manifest.csv',{'missing':sorted(listed-actual),'extra':sorted(actual-listed)})
        for r in manifest:
            p=ROOT/r['path']
            if p.is_file() and (p.stat().st_size!=int(r['bytes']) or sha256(p)!=r['sha256']):err('manifest_hash',r['path'])
    print(json.dumps({'status':'pass' if not errors else 'fail','files_checked':len(files),'counts':counts,'errors':errors},ensure_ascii=False,indent=2))
    return bool(errors)
if __name__=='__main__':raise SystemExit(main())
