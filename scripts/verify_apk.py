"""Verify an actual ppplayer APK contains the locally packaged native libraries."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('apk', type=Path)
parser.add_argument('--artifacts', type=Path, default=root / 'artifacts')
parser.add_argument('--package', type=Path,
                    help='Verify against a self-contained published plugin instead of local build artifacts')
parser.add_argument('--abi', action='append', choices=['arm64-v8a', 'x86_64'],
                    help='Check selected runtime ABI; by default check both release ABIs')
args = parser.parse_args()
manifest_path = (args.package / 'android/native-manifest.json' if args.package
                 else args.artifacts / 'manifest.json')
jar_dir = args.package / 'android/libs' if args.package else args.artifacts
lock_path = (args.package / 'native_sources/sources.lock.json' if args.package
             else root / 'sources.lock.json')
manifest = json.loads(manifest_path.read_text())
if manifest.get('format') != 1 or set(manifest['abis']) != {'arm64-v8a', 'x86_64'}:
    raise RuntimeError('A complete two-architecture artifact manifest is required')
sha = lambda data: hashlib.sha256(data).hexdigest()
if sha(lock_path.read_bytes().replace(b'\r\n', b'\n')) != manifest['sources_lock_sha256']:
    raise RuntimeError('Artifacts do not match the source lock')
with zipfile.ZipFile(args.apk) as archive:
    for abi, metadata in manifest['abis'].items():
        if args.abi and abi not in args.abi:
            continue
        if sha((jar_dir / metadata['file']).read_bytes()) != metadata['sha256']:
            raise RuntimeError(f'JAR checksum mismatch: {abi}')
        for library, field in (('libmpv.so', 'libmpv_sha256'),
                               ('libmediakitandroidhelper.so', 'helper_sha256')):
            name = f'lib/{abi}/{library}'
            if sha(archive.read(name)) != metadata[field]:
                raise RuntimeError(f'APK contains a different native binary: {name}')
            print(f'Verified bundled binary: {name}')
print(f'APK matches local native artifacts: {args.apk}')
