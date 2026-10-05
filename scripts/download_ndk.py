"""Resume the pinned NDK with verified HTTP byte ranges and a final archive hash."""
import concurrent.futures
import hashlib
from pathlib import Path
import shutil
import sys
import urllib.request

ROOT = Path(__file__).resolve().parent.parent
URL = 'https://dl.google.com/android/repository/android-ndk-r27d-linux.zip'
SIZE = 663956036
SHA1 = '22105e410cf29afcf163760cc95522b9fb981121'
archive = ROOT / 'buildscripts/sdk/downloads/android-ndk-r27d-linux.zip'

def request(start, end):
    return urllib.request.Request(URL, headers={'Range': f'bytes={start}-{end}', 'Accept-Encoding': 'identity'})

if '--probe' in sys.argv:
    with urllib.request.urlopen(request(0, 0), timeout=15) as response:
        print(response.status, response.headers.get('Content-Range'), response.read(2).hex())
    sys.exit(0)

archive.parent.mkdir(parents=True, exist_ok=True)
offset = archive.stat().st_size if archive.exists() else 0
if offset > SIZE:
    raise RuntimeError('Existing NDK archive exceeds pinned size')
chunks = ROOT / '.work/ndk-ranges'
chunks.mkdir(parents=True, exist_ok=True)
ranges = [(start, min(start + 16 * 1024 * 1024, SIZE) - 1)
          for start in range(offset, SIZE, 16 * 1024 * 1024)]

def download(bounds):
    start, end = bounds
    path = chunks / f'{start}-{end}.part'
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request(start, end), timeout=60) as response:
                expected = f'bytes {start}-{end}/{SIZE}'
                if response.status != 206 or response.headers.get('Content-Range') != expected:
                    raise RuntimeError('Server did not honor the requested byte range')
                with path.open('wb') as target:
                    shutil.copyfileobj(response, target, length=1024 * 1024)
            if path.stat().st_size != end - start + 1:
                raise RuntimeError('Incomplete NDK byte range')
            print(f'Range complete: {start}-{end}', flush=True)
            return path
        except Exception:
            if attempt == 2:
                raise

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    parts = list(executor.map(download, ranges))
with archive.open('ab') as target:
    for part in parts:
        with part.open('rb') as source:
            shutil.copyfileobj(source, target)
with archive.open('rb') as source:
    actual = hashlib.file_digest(source, 'sha1').hexdigest()
if actual != SHA1:
    raise RuntimeError(f'Pinned NDK archive checksum mismatch: {actual}')
print('Pinned NDK archive verified.', flush=True)
