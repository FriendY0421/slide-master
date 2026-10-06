#!/usr/bin/env python3
"""PPT Master - Private font inventory and cache.

Inspect exact face metadata; copy consented fonts into private owner/endpoint
roots with portable relative paths. Storage never installs or activates fonts.

Usage: python3 scripts/private_font_cache.py inspect FONT
Examples: python3 scripts/private_font_cache.py verify --root projects/private/fonts
Dependencies: fontTools (existing runtime; never installed by this script)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import unicodedata
from pathlib import Path

from console_encoding import configure_utf8_stdio

configure_utf8_stdio()
REPO_ROOT = Path(__file__).resolve().parents[4]


def _label(value: str) -> str:
    return ''.join(unicodedata.normalize('NFKC', value).casefold().split())


def lookup_font_entries(request: dict, entries: list[dict]) -> dict:
    """Find localized names/aliases; lock only an unambiguous verified face."""
    query = _label(request['family'])
    found, personal = [], []
    for entry in entries:
        names = [entry.get('family')] + entry.get('aliases', []) + entry.get('search_aliases', [])
        locks = [a for a in entry.get('personal_aliases', []) if isinstance(a, dict)
                 and _label(a.get('name', '')) == query and a.get('user_confirmed') is True
                 and a.get('sha256') == entry.get('sha256')]
        if not locks and query not in [_label(str(v)) for v in names if v]:
            continue
        if any(request.get(k) and entry.get(k) and _label(str(request[k])) != _label(str(entry[k]))
               for k in ('style', 'version', 'sha256')):
            continue
        found.append(entry)
        if locks:
            personal.append(entry)
    candidates = personal or found
    ambiguous = len(candidates) != 1 or (query in {'고딕', '견고딕'} and not personal and not request.get('sha256'))
    selected = candidates[0] if candidates and not ambiguous else None
    if selected and (selected.get('verification_level') != 'hash_verified' or selected.get('status') != 'available'):
        selected = None
    return {'candidates': candidates, 'selected': selected,
            'needs_first_confirmation': bool(candidates) and selected is None,
            'personal_alias_reused': bool(personal) and selected is not None}


def inspect_font(path: Path) -> dict:
    """Read family/style/version and exact bytes, without installing a face."""
    if path.suffix.lower() not in {'.ttf', '.otf'}:
        raise ValueError('TTC requires explicit face/support verification; FON/other format renderer support unverified; no conversion or installation')
    try:
        from fontTools.ttLib import TTFont, TTLibError
    except ImportError as exc:
        raise ValueError("Font metadata runtime unavailable; provide prepared fontTools runtime") from exc
    try:
        face = TTFont(path, lazy=True)
    except TTLibError as exc:
        raise ValueError('Invalid font binary; request a supported font file') from exc
    with face:
        def name(primary, fallback):
            return face['name'].getDebugName(primary) or face['name'].getDebugName(fallback)
        def aliases(ids):
            names = set()
            for item in face['name'].names:
                if item.nameID in ids:
                    try:
                        names.add(item.toUnicode())
                    except UnicodeDecodeError:
                        continue
            return sorted(names)
        result = {"verification_level": "hash_verified", "renderer_support": "unverified", "family_aliases": aliases({1, 16}), "style_aliases": aliases({2, 17}),
                  "family": name(16, 1), "style": name(17, 2), "version": name(5, 5),
                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size,
                  "fsType": face['OS/2'].fsType if 'OS/2' in face else None}
    if not all(result[k] for k in ('family', 'style', 'version')):
        raise ValueError("Unverified font metadata; request an identifiable font file")
    return result


def _private_root(path: Path) -> Path:
    root = path.resolve()
    if root.is_relative_to(REPO_ROOT) and not root.is_relative_to(REPO_ROOT / 'projects'):
        raise ValueError("Font cache must be outside the public repo or in gitignored projects/")
    return root


def _relative_file(root: Path, relative: str) -> Path:
    raw = Path(relative)
    target = (root / raw).resolve()
    if raw.is_absolute() or not target.is_relative_to(root.resolve()):
        raise ValueError("Cache manifest paths must stay relative to the supplied private root")
    return target


def verify_cache(root: Path, endpoint: str) -> dict:
    """Re-resolve a relocated cache and verify metadata, hashes and permissions."""
    root = _private_root(root)
    manifest = json.loads((root / 'font-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('schema_version') != 1 or manifest.get('reuse_confirmed') is not True:
        raise ValueError("Missing consented v1 cache manifest")
    policy = manifest['license_review']
    if policy.get('reviewed') is not True or policy.get('copy') != 'allowed':
        raise ValueError("Copy license not confirmed")
    if endpoint == 'cloud' and policy.get('cloud_use') != 'allowed':
        raise ValueError("Cloud font use not licensed or unknown")
    if policy.get('embedding') not in {'allowed', 'denied', 'unknown'}:
        raise ValueError("Embedding license scope must be recorded separately")
    license_file = _relative_file(root, policy['path'])
    if hashlib.sha256(license_file.read_bytes()).hexdigest() != policy['sha256']:
        raise ValueError("License evidence hash mismatch")
    records = manifest.get('fonts', [])
    if not records:
        raise ValueError("No cached font faces")
    for record in records:
        actual = inspect_font(_relative_file(root, record['path']))
        if any(actual[k] != record.get(k) for k in actual):
            raise ValueError("Cached font bytes or metadata changed")
    return {"manifest": manifest, "endpoint": endpoint, "stored_verified": True,
            "system_installed": False, "render_activated": False, "embedded": False}


def store_fonts(fonts: list[Path], license_file: Path, policy: dict,
                owner_root: Path, endpoint_root: Path, endpoint: str, consent: bool) -> dict:
    """Store reusable files only after explicit reuse and license review."""
    if not consent:
        raise ValueError("User reuse consent required; keep task-only files without persistent caching")
    owner_root, endpoint_root = _private_root(owner_root), _private_root(endpoint_root)
    if owner_root == endpoint_root:
        raise ValueError("Owner storage and endpoint cache must be distinct roots")
    if policy.get('reviewed') is not True or policy.get('copy') != 'allowed':
        raise ValueError("Review font copying license before private caching")
    if endpoint == 'cloud' and policy.get('cloud_use') != 'allowed':
        raise ValueError("Cloud use is denied or unknown; no font copied")
    if policy.get('embedding') not in {'allowed', 'denied', 'unknown'}:
        raise ValueError("Record embedding permission even though this tool does not embed")
    records = []
    for path in fonts:
        metadata = inspect_font(path)
        metadata['path'] = 'fonts/' + metadata['sha256'] + path.suffix.lower()
        records.append(metadata)
    if not records:
        raise ValueError("At least one font face required")
    license_bytes = license_file.read_bytes()
    license_sha = hashlib.sha256(license_bytes).hexdigest()
    if policy.get('evidence_sha256') != license_sha:
        raise ValueError("License review must bind the exact evidence_sha256")
    manifest = {"schema_version": 1, "scope": "user-private", "reuse_confirmed": True,
                "fonts": records, "license_review": {**policy, 'path': 'licenses/' + license_sha + '.txt', 'sha256': license_sha},
                "root_contract": "Resolve relative files under caller-supplied owner or endpoint root",
                "system_installation": "not performed", "render_activation": "requires explicit runtime registration and QA",
                "embedding": "not performed"}
    # Preflight collisions before any write; previous cache never disappears.
    for root in (owner_root, endpoint_root):
        manifest_path = root / 'font-manifest.json'
        if manifest_path.exists():
            raise ValueError("Cache already exists; verify/sync it or choose a new private root")
        for record in records:
            if _relative_file(root, record['path']).exists():
                raise ValueError("Font destination already exists")
    for root in (owner_root, endpoint_root):
        root.mkdir(parents=True, exist_ok=True, mode=0o700)
        for path, record in zip(fonts, records):
            target = _relative_file(root, record['path']);target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copyfile(path, target);target.chmod(0o600)
        target = _relative_file(root, manifest['license_review']['path']);target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        target.write_bytes(license_bytes);target.chmod(0o600)
        (root / 'font-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        (root / 'font-manifest.json').chmod(0o600)
    return verify_cache(endpoint_root, endpoint)


def sync_cache(owner_root: Path, endpoint_root: Path, endpoint: str) -> dict:
    """Materialize a private endpoint cache from verified owner storage."""
    source = verify_cache(owner_root, endpoint);target = _private_root(endpoint_root)
    if target.exists():
        existing = verify_cache(target, endpoint)
        if existing['manifest'] != source['manifest']:
            raise ValueError("Endpoint manifest differs; never overwrite another cache")
        return existing
    target.mkdir(parents=True, mode=0o700)
    manifest=source['manifest']
    for relative in [f['path'] for f in manifest['fonts']]+[manifest['license_review']['path'],'font-manifest.json']:
        destination=_relative_file(target,relative);destination.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        shutil.copyfile(_relative_file(_private_root(owner_root),relative),destination);destination.chmod(0o600)
    return verify_cache(target, endpoint)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    inspect = sub.add_parser('inspect');inspect.add_argument('font', type=Path)
    store = sub.add_parser('store');store.add_argument('fonts', type=Path, nargs='+')
    store.add_argument('--license-file', type=Path, required=True);store.add_argument('--license-policy', type=Path, required=True)
    store.add_argument('--owner-root', type=Path, required=True);store.add_argument('--endpoint-root', type=Path, required=True)
    store.add_argument('--reuse-confirmed', action='store_true')
    sync = sub.add_parser('sync');sync.add_argument('--owner-root', type=Path, required=True);sync.add_argument('--endpoint-root', type=Path, required=True)
    verify = sub.add_parser('verify');verify.add_argument('--root', type=Path, required=True)
    for command in (store, sync, verify):
        command.add_argument('--endpoint', choices=('local', 'cloud'), required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'inspect': result = inspect_font(args.font)
        elif args.command == 'store': result = store_fonts(args.fonts, args.license_file, json.loads(args.license_policy.read_text(encoding='utf-8')), args.owner_root, args.endpoint_root, args.endpoint, args.reuse_confirmed)
        elif args.command == 'sync': result = sync_cache(args.owner_root, args.endpoint_root, args.endpoint)
        else: result = verify_cache(args.root, args.endpoint)
        print(json.dumps(result, ensure_ascii=False, indent=2));return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('Font cache blocked: ' + str(exc), file=sys.stderr);return 1


def font_availability(brief: dict, base: Path) -> dict:
    """Inspect declared/private/system files on this endpoint, with no fallback."""
    from preflight import _font_dirs, FONT_SCAN_CAP
    requests=brief.get('font_requests',[])
    matching=brief.get('font_matching',{})
    if not requests and isinstance(matching,dict) and matching.get('user_confirmed') is True and matching.get('similarity_approved') is True:
        selected=matching.get('selected',{})
        requests=[{k:v for k,v in selected.items() if k in {'family','style','version','sha256'}}]
    families=brief.get('font_families',[])
    policy=brief.get('font_policy',{})
    policy=policy if isinstance(policy,dict) else {}
    if not requests:
        if not families and policy.get('basis')=='specified': families=list(dict.fromkeys(policy.get('values',{}).values()))
        requests=[{'family':family} for family in families]
    if not isinstance(requests,list) or any(not isinstance(r,dict) or not isinstance(r.get('family'),str) or not r['family'].strip() for r in requests):
        return {'ok':False,'errors':['Declare required family/style'], 'question':'사용할 글꼴 family/style과 폰트 파일을 확인해 주세요.'}
    requests=[dict(request) for request in requests]
    # The current policy is authoritative even when an older font_requests list
    # remains in the brief. Additional exact face constraints still apply.
    required_families = list(families)
    if policy.get('basis') == 'specified':
        required_families.extend(policy.get('values', {}).values())
    for family in required_families:
        if not isinstance(family, str) or not family.strip():
            return {'ok': False, 'errors': ['Invalid effective font family'],
                    'question': '현재 지정 글꼴을 확인해 주세요.'}
        if not any(_label(r['family']) == _label(family) for r in requests):
            requests.append({'family': family})
    effective_requests = [dict(request) for request in requests]
    requirement_sha256 = hashlib.sha256(json.dumps(
        {'font_policy': policy, 'requests': effective_requests},
        ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    paths=[];errors=[];records=[];licensed=set();library_candidates=[];alias_resolutions=[]
    for raw in brief.get('font_files',[]): paths.append(Path(raw) if Path(raw).is_absolute() else base/raw)
    caches=list(brief.get('font_cache_roots',[]))
    if brief.get('font_library_file'):
        try:
            library_file=Path(brief['font_library_file']);library_file=library_file if library_file.is_absolute() else base/library_file
            library=json.loads(library_file.read_text(encoding='utf-8'))
            library_root=Path(brief.get('font_library_root',library_file.parent));library_root=library_root if library_root.is_absolute() else base/library_root
            library_root=_private_root(library_root)
            if library.get('schema_version')!=1 or library.get('scope')!='user-private': raise ValueError('Invalid private library mapping')
            for index, request in enumerate(requests):
                lookup=lookup_font_entries(request,library.get('entries',[]))
                entry=lookup['selected']
                if not entry:
                    library_candidates.extend({k:candidate.get(k) for k in ('family','style','filename','bytes','verification_level','status')} for candidate in lookup['candidates'])
                    if lookup['needs_first_confirmation']:
                        errors.append('Preview and first confirmation required for font candidates: '+request['family'])
                    continue
                cache=_relative_file(library_root,entry['cache_entry'])
                manifest=verify_cache(cache,brief.get('endpoint','cloud'))['manifest']
                if not any(f['sha256']==entry.get('sha256') for f in manifest['fonts']): raise ValueError('Library hash differs from actual cache')
                caches.append(str(cache))
                face=next(f for f in manifest['fonts'] if f['sha256']==entry['sha256'])
                requests[index]={k:face[k] for k in ('family','style','version','sha256')}
                alias_resolutions.append({'requested':request['family'],'family':face['family'],'sha256':face['sha256'],'personal_alias_reused':lookup['personal_alias_reused']})
        except (OSError,ValueError,KeyError,TypeError) as exc: errors.append(str(exc))
    if brief.get('font_cache_root'): caches=[brief['font_cache_root']]+caches
    for raw in caches:
        cache=Path(raw);cache=cache if cache.is_absolute() else base/cache
        try:
            manifest=verify_cache(cache,brief.get('endpoint','cloud'))['manifest']
            paths.extend(_relative_file(cache,f['path']) for f in manifest['fonts'])
            licensed.update(f['sha256'] for f in manifest['fonts'])
        except (OSError,ValueError,KeyError,TypeError) as exc: errors.append(str(exc))
    license_review=brief.get('font_license_review',{})
    if isinstance(license_review,dict) and license_review.get('reviewed') is True:
        try:
            evidence=Path(license_review['evidence_file']);evidence=evidence if evidence.is_absolute() else base/evidence
            if hashlib.sha256(evidence.read_bytes()).hexdigest()!=license_review.get('evidence_sha256'):
                raise ValueError('Font license evidence hash mismatch')
            if brief.get('endpoint','cloud')=='cloud' and license_review.get('cloud_use')!='allowed':
                raise ValueError('Cloud use license is denied or unknown')
            if license_review.get('embedding') not in {'allowed','denied','unknown'}:
                raise ValueError('Record font embedding license scope')
            licensed.update(license_review.get('font_sha256',[]))
        except (OSError,ValueError,KeyError,TypeError) as exc: errors.append(str(exc))
    for path in dict.fromkeys(paths):
        try: records.append({**inspect_font(path),'source':'provided/private-cache','file':str(path)})
        except (OSError,ValueError,KeyError) as exc: errors.append(str(exc))
    # Check actual binary metadata instead of assuming that a filename/registry
    # label proves the requested face/version. Cap scans and leave unknown missing.
    seen=0
    for root in _font_dirs():
        for path in root.rglob('*'):
            if path.suffix.lower() not in {'.otf','.ttf'}: continue
            seen+=1
            if seen>FONT_SCAN_CAP: break
            try: record=inspect_font(path)
            except (OSError,ValueError,KeyError): continue
            if any(r['family'].casefold() in [v.casefold() for v in record['family_aliases']] for r in requests):
                records.append({**record,'source':'system-file','file':str(path)})
        if seen>FONT_SCAN_CAP: break
    missing=[]; verified_faces=[]
    for request in requests:
        def matches(record):
            for key, value in request.items():
                if key in {'family', 'style'}:
                    if _label(str(value)) not in [_label(v) for v in record[key+'_aliases']]:
                        return False
                elif key in {'version', 'sha256'} and str(record.get(key, '')).casefold() != str(value).casefold():
                    return False
            return True
        matched=[record for record in records if matches(record)]
        verified_faces.extend({k: record[k] for k in ('family', 'style', 'version', 'sha256')}
                              for record in matched if record['sha256'] in licensed)
        if not matched: missing.append(request)
        elif not any(record['sha256'] in licensed for record in matched): errors.append('Font license review required: '+request['family'])
        if _label(request['family']) in {'고딕','견고딕'} and not request.get('sha256'):
            errors.append('Generic font term requires preview and explicit face confirmation: '+request['family'])
        faces={}
        for record in matched:
            faces.setdefault((_label(record['family']),_label(record['style'])),set()).add(record['sha256'])
        if not request.get('sha256') and any(len(hashes)>1 for hashes in faces.values()):
            errors.append('Multiple versions/vendors require preview and first confirmation: '+request['family'])
    if not requests: errors.append('Source/inherited font families have not been identified; request/confirm actual font files')
    return {'ok':bool(requests) and not errors and not missing, 'endpoint':brief.get('endpoint','cloud'),
            'effective_requests': effective_requests, 'requirement_sha256': requirement_sha256,
            'verified_faces': verified_faces,
            'records':records,'licensed_font_sha256':sorted(licensed),'font_library_candidates':library_candidates,'alias_resolutions':alias_resolutions,'missing_fonts':missing,'errors':errors,'scan_truncated':seen>FONT_SCAN_CAP,
            'question':'누락되거나 확인할 수 없는 글꼴의 폰트 파일과 사용 라이선스를 추가해 주세요.' if missing or errors else None,
            'render_activated':False,'system_installation_performed':False,'silent_fallback':False,'library_status':'missing' if missing else 'license_review_required' if errors else 'available'}


if __name__ == '__main__':
    raise SystemExit(main())
