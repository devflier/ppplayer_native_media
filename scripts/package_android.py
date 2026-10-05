"""Package built mpv with the exact upstream JNI helper; emit verified local JARs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parent.parent
HELPERS = {
    'arm64-v8a': '83df25b61193af8fa815e373143ac9af',
    'x86_64': '6fa26bf0459b11f1c0b0dbc29e5b940d',
}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--abi', choices=HELPERS, required=True)
    parser.add_argument('--helper-jars', type=Path, default=ROOT / '.work/helper-jars')
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts')
    args = parser.parse_args()
    source = ROOT / 'buildscripts/prefix' / args.abi / 'lib/libmpv.so'
    if not source.is_file():
        parser.error(f'Native build missing: {source}')
    ndk = ROOT / 'buildscripts/sdk/android-sdk-linux/ndk/27.3.13750724/toolchains/llvm/prebuilt/linux-x86_64/bin'
    symbols = subprocess.check_output([str(ndk / 'llvm-nm'), '-D', '--defined-only', str(source)], text=True)
    for symbol in ('mpv_create', 'mpv_initialize', 'mpv_wait_event', 'mpv_lavc_set_java_vm'):
        if not any(line.split()[-1] == symbol for line in symbols.splitlines() if line.split()):
            raise RuntimeError(f'Missing required native symbol: {symbol}')
    headers = subprocess.check_output([str(ndk / 'llvm-readelf'), '-lW', str(source)], text=True)
    loads = [line.split() for line in headers.splitlines() if line.strip().startswith('LOAD ')]
    if not loads or any(int(line[-1], 16) < 0x4000 for line in loads):
        raise RuntimeError('Native ELF does not meet 16 KiB LOAD alignment')
    dynamic = subprocess.check_output([str(ndk / 'llvm-readelf'), '-dW', str(source)], text=True)
    needed = set(re.findall(r'\(NEEDED\).*\[([^]]+)\]', dynamic))
    system_libs = {'libandroid.so', 'liblog.so', 'libEGL.so', 'libGLESv2.so',
                   'libGLESv3.so', 'libOpenSLES.so', 'libmediandk.so',
                   'libc.so', 'libm.so', 'libdl.so', 'libz.so'}
    if needed - system_libs:
        raise RuntimeError(f'Unbundled native dependencies: {sorted(needed - system_libs)}')
    args.helper_jars.mkdir(parents=True, exist_ok=True)
    helper_jar = args.helper_jars / f'default-{args.abi}.jar'
    if not helper_jar.exists():
        url = f'https://github.com/media-kit/libmpv-android-video-build/releases/download/v1.1.7/{helper_jar.name}'
        urllib.request.urlretrieve(url, helper_jar)
    upstream = helper_jar.read_bytes()
    if hashlib.md5(upstream).hexdigest() != HELPERS[args.abi]:
        raise RuntimeError(f'Upstream helper JAR checksum mismatch: {helper_jar}')
    with zipfile.ZipFile(helper_jar) as archive:
        helper = archive.read(f'lib/{args.abi}/libmediakitandroidhelper.so')
    check_dir = ROOT / '.work/helper-check'
    check_dir.mkdir(parents=True, exist_ok=True)
    helper_so = check_dir / f'helper-{args.abi}.so'
    helper_so.write_bytes(helper)
    helper_headers = subprocess.check_output([str(ndk / 'llvm-readelf'), '-lW', str(helper_so)], text=True)
    helper_loads = [line.split() for line in helper_headers.splitlines() if line.strip().startswith('LOAD ')]
    if not helper_loads or any(int(line[-1], 16) < 0x4000 for line in helper_loads):
        raise RuntimeError('Upstream JNI helper does not meet 16 KiB LOAD alignment')
    args.output.mkdir(parents=True, exist_ok=True)
    # Keep unstripped build outputs intact for debugging.
    stripped = args.output / f'libmpv-{args.abi}.so'
    shutil.copyfile(source, stripped)
    subprocess.run([str(ndk / 'llvm-strip'), '--strip-all', str(stripped)], check=True)
    native = stripped.read_bytes()
    jar = args.output / f'ppplayer-{args.abi}.jar'
    with zipfile.ZipFile(jar, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in ((f'lib/{args.abi}/libmpv.so', native),
                           (f'lib/{args.abi}/libmediakitandroidhelper.so', helper)):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(entry, data)
    manifest_path = args.output / 'manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {'format': 1, 'abis': {}}
    lock_hash = digest((ROOT / 'sources.lock.json').read_bytes())
    if manifest['abis'] and manifest.get('sources_lock_sha256') != lock_hash:
        raise RuntimeError('Existing artifacts have a different source lock; select a new output directory')
    manifest['sources_lock_sha256'] = lock_hash
    manifest['abis'][args.abi] = {'file': jar.name, 'sha256': digest(jar.read_bytes()),
                                'libmpv_sha256': digest(native), 'helper_sha256': digest(helper)}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Verified package: {jar}')

if __name__ == '__main__':
    main()
