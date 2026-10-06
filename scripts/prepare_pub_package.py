"""Verify release binaries and bundle pinned corresponding sources for pub.dev."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / 'packages/flutter_media_kit'
URLS = {
    'dav1d': 'https://code.videolan.org/videolan/dav1d.git',
    'ffmpeg': 'https://github.com/FFmpeg/FFmpeg.git',
    'freetype': 'https://gitlab.freedesktop.org/freetype/freetype.git',
    'fribidi': 'https://github.com/fribidi/fribidi.git',
    'harfbuzz': 'https://github.com/harfbuzz/harfbuzz.git',
    'libass': 'https://github.com/libass/libass.git',
    'libxml2': 'https://gitlab.gnome.org/GNOME/libxml2.git',
    'mbedtls': 'https://github.com/Mbed-TLS/mbedtls.git',
    'mpv': 'https://github.com/mpv-player/mpv.git',
}
LICENSES = {
    'dav1d': ['COPYING'],
    'ffmpeg': ['LICENSE.md', 'COPYING.LGPLv3', 'COPYING.LGPLv2.1', 'COPYING.GPLv3'],
    'freetype': ['LICENSE.TXT', 'docs/FTL.TXT'],
    'fribidi': ['COPYING'],
    'harfbuzz': ['COPYING'],
    'libass': ['COPYING'],
    'libxml2': ['Copyright'],
    'mbedtls': ['LICENSE'],
    'mpv': ['Copyright', 'LICENSE.LGPL'],
}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def text_bytes(path):
    return path.read_bytes().replace(b'\r\n', b'\n')

def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args])

def verify(package):
    manifest = json.loads((package / 'android/native-manifest.json').read_text())
    lock = (package / 'native_sources/sources.lock.json').read_bytes()
    if sha(lock) != manifest['sources_lock_sha256']:
        raise RuntimeError('Packaged source lock checksum mismatch')
    if set(manifest['abis']) != {'arm64-v8a', 'x86_64'}:
        raise RuntimeError('Release requires both Android architectures')
    for abi, entry in manifest['abis'].items():
        jar = package / 'android/libs' / entry['file']
        if sha(jar.read_bytes()) != entry['sha256']:
            raise RuntimeError(f'JAR checksum mismatch: {abi}')
        with zipfile.ZipFile(jar) as archive:
            for lib, field in [('libmpv.so', 'libmpv_sha256'),
                               ('libmediakitandroidhelper.so', 'helper_sha256')]:
                if sha(archive.read(f'lib/{abi}/{lib}')) != entry[field]:
                    raise RuntimeError(f'Native library checksum mismatch: {abi}/{lib}')

def add_bytes(archive, name, data, executable=False):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o755 if executable else 0o644
    info.mtime = info.uid = info.gid = 0
    archive.addfile(info, io.BytesIO(data))

def bundle_tree(archive, repo, commit, prefix):
    data = git(repo, 'archive', '--format=tar', commit)
    with tarfile.open(fileobj=io.BytesIO(data)) as upstream:
        for member in upstream:
            if member.name.startswith('/') or '..' in Path(member.name).parts:
                raise RuntimeError('Unsafe source archive path')
            payload = upstream.extractfile(member) if member.isfile() else None
            member.name = f'{prefix}/{member.name}'
            member.mtime = member.uid = member.gid = 0
            member.uname = member.gname = ''
            archive.addfile(member, payload)
    submodules = [line for line in git(repo, 'ls-tree', '-r', commit).decode().splitlines()
                  if line.startswith('160000 ')]
    if submodules:
        paths = git(repo, 'config', '--blob', commit + ':.gitmodules',
                    '--get-regexp', r'^submodule\..*\.path$').decode().splitlines()
        keys = {line.split(' ', 1)[1]: line.split(' ', 1)[0][:-5] for line in paths}
        for line in submodules:
            metadata, path = line.split('\t', 1)
            subcommit = metadata.split()[2]
            url = git(repo, 'config', '--blob', commit + ':.gitmodules',
                      '--get', keys[path] + '.url').decode().strip()
            if not url.startswith('https://'):
                raise RuntimeError(f'Unsupported submodule URL: {url}')
            checkout = ROOT / '.work/pub-submodules' / subcommit
            if not (checkout / '.git').exists():
                checkout.mkdir(parents=True, exist_ok=True)
                subprocess.run(['git', 'init', str(checkout)], check=True)
                subprocess.run(['git', '-C', str(checkout), 'fetch', '--depth=1', url, subcommit], check=True)
            bundle_tree(archive, checkout, subcommit, f'{prefix}/{path}')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources-root', type=Path, default=ROOT / '.work/pub-sources')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--package', type=Path, default=PACKAGE)
    args = parser.parse_args()
    if args.verify_only:
        verify(args.package)
        source = args.package / 'native_sources/corresponding-source.tar.gz'
        record = json.loads((args.package / 'native_sources/archive.json').read_text())
        if sha(source.read_bytes()) != record['sha256']:
            raise RuntimeError('Corresponding source archive checksum mismatch')
        print('Both native JARs, inner libraries, source lock and source archive verified.')
        return
    if args.package != PACKAGE:
        parser.error('--package is only supported with --verify-only')
    lock_bytes = text_bytes(ROOT / 'sources.lock.json')
    lock = json.loads(lock_bytes)
    for field in ['patches_sha256', 'recipes_sha256']:
        for name, expected in lock[field].items():
            if sha(text_bytes(ROOT / name)) != expected:
                raise RuntimeError(f'Locked build input differs: {name}')
    source_dir = PACKAGE / 'native_sources'
    source_dir.mkdir(exist_ok=True)
    (source_dir / 'sources.lock.json').write_bytes(lock_bytes)
    verify(PACKAGE)
    licenses = PACKAGE / 'licenses'
    licenses.mkdir(exist_ok=True)
    output = source_dir / 'corresponding-source.tar.gz'
    temporary = output.with_suffix('.tmp')
    with temporary.open('wb') as file:
        with gzip.GzipFile(filename='', mode='wb', fileobj=file, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|') as archive:
                add_bytes(archive, 'sources.lock.json', lock_bytes)
                for name, commit in sorted(lock['sources'].items()):
                    repo = args.sources_root / name
                    if not (repo / '.git').exists():
                        repo.mkdir(parents=True, exist_ok=True)
                        subprocess.run(['git', 'init', str(repo)], check=True)
                        subprocess.run(['git', '-C', str(repo), 'fetch', '--depth=1', URLS[name], commit], check=True)
                    git(repo, 'cat-file', '-e', commit + '^{commit}')
                    bundle_tree(archive, repo, commit, f'buildscripts/deps/{name}')
                    for filename in LICENSES[name]:
                        content = git(repo, 'show', f'{commit}:{filename}')
                        (licenses / f'{name}-{filename.replace("/", "-")}').write_bytes(content)
                    print(f'Bundled {name} at {commit}', flush=True)
                inputs = set(lock['patches_sha256']) | set(lock['recipes_sha256'])
                inputs |= {'scripts/build_android.sh', 'scripts/package_android.py',
                           'scripts/bootstrap_android.sh', 'scripts/test_egl_fallback.py'}
                for name in sorted(inputs):
                    add_bytes(archive, name, text_bytes(ROOT / name), name.endswith('.sh'))
                add_bytes(archive, 'README.md', text_bytes(source_dir / 'README.md'))
    temporary.replace(output)
    (source_dir / 'archive.json').write_text(json.dumps({
        'file': output.name, 'sha256': sha(output.read_bytes()),
        'sources_lock_sha256': sha(lock_bytes),
    }, indent=2) + '\n')
    print(f'Prepared source archive: {output.stat().st_size / 1048576:.1f} MiB')

if __name__ == '__main__':
    main()
