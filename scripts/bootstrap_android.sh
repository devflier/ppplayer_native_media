#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT/buildscripts"
mkdir -p sdk/downloads sdk/android-sdk-linux/ndk deps
NDK_ZIP=sdk/downloads/android-ndk-r27d-linux.zip
NDK_SHA1=22105e410cf29afcf163760cc95522b9fb981121
if [ ! -d sdk/android-sdk-linux/ndk/27.3.13750724 ]; then
  if [ ! -f "$NDK_ZIP" ]; then
    curl -fL --retry 3 https://dl.google.com/android/repository/android-ndk-r27d-linux.zip -o "$NDK_ZIP"
  fi
  echo "$NDK_SHA1  $NDK_ZIP" | sha1sum --check
  unzip -q "$NDK_ZIP" -d sdk/downloads
  mv sdk/downloads/android-ndk-r27d sdk/android-sdk-linux/ndk/27.3.13750724
fi

fetch() {
  local name=$1 url=$2 ref=$3
  if [ ! -d "deps/$name/.git" ]; then
    git init "deps/$name"
    git -C "deps/$name" remote add origin "$url"
    git -C "deps/$name" fetch --depth 1 origin "$ref"
    git -C "deps/$name" checkout --detach FETCH_HEAD
  fi
}
fetch mbedtls https://github.com/Mbed-TLS/mbedtls.git v3.4.0
fetch dav1d https://code.videolan.org/videolan/dav1d.git 1.2.0
fetch libxml2 https://gitlab.gnome.org/GNOME/libxml2.git v2.10.3
fetch ffmpeg https://github.com/FFmpeg/FFmpeg.git n6.0
fetch freetype https://gitlab.freedesktop.org/freetype/freetype.git VER-2-13-0
fetch fribidi https://github.com/fribidi/fribidi.git v1.0.12
fetch harfbuzz https://github.com/harfbuzz/harfbuzz.git 7.2.0
fetch libass https://github.com/libass/libass.git 0.17.1
fetch mpv https://github.com/mpv-player/mpv.git 78d43740f52db817d98bcf24fb30a76ab6fa13ff

# Apply only tracked patches; do not reset or delete dependency checkouts.
for patch in patches/ffmpeg/*.patch patches/mpv/*.patch patches/mbedtls/*.patch; do
  dep=$(basename "$(dirname "$patch")")
  if git -C "deps/$dep" apply --reverse --check "$PWD/$patch" 2>/dev/null; then
    continue
  fi
  git -C "deps/$dep" apply --check "$PWD/$patch"
  git -C "deps/$dep" apply "$PWD/$patch"
done
cp flavors/default.sh scripts/ffmpeg.sh
chmod +x build.sh scripts/*.sh
python3 - "$ROOT" <<'PY'
import hashlib, json, pathlib, subprocess, sys
root = pathlib.Path(sys.argv[1])
sources = {}
for path in sorted((root / 'buildscripts/deps').iterdir()):
    if (path / '.git').is_dir():
        sources[path.name] = subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()
lock_path = root / 'sources.lock.json'
if lock_path.exists():
    expected = json.loads(lock_path.read_text())['sources']
    if sources != expected:
        raise RuntimeError('Dependency commits differ from the recorded source lock; inspect the checkouts')
patches = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((root / 'buildscripts/patches').glob('*/*.patch'))}
data = {'upstream_native_build': 'fe8c3ac1a91c09aa6fb1deccbc833f1bafa54768',
        'ndk': '27.3.13750724', 'ndk_archive_sha1': '22105e410cf29afcf163760cc95522b9fb981121',
        'sources': sources, 'patches_sha256': patches}
recipes = [root / 'buildscripts/build.sh', root / 'buildscripts/include/depinfo.sh',
           root / 'buildscripts/include/path.sh', root / 'buildscripts/flavors/default.sh']
recipes += sorted((root / 'buildscripts/scripts').glob('*.sh'))
# ffmpeg.sh is generated from the default flavor during bootstrap.
data['recipes_sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in recipes if p.name != 'ffmpeg.sh'}
(root / 'sources.lock.json').write_text(json.dumps(data, indent=2) + '\n')
PY
echo 'Android sources and NDK ready.'
