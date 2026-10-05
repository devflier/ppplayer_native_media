"""Backport upstream Mbed TLS PR 7878 to the pinned 3.4.0 source."""
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent.parent
repo = root / 'buildscripts/deps/mbedtls'
source = repo / 'library/aesce.c'
text = source.read_text()
before = '__attribute__((target("crypto")))'
after = '__attribute__((target("aes")))'
if before in text:
    source.write_text(text.replace(before, after, 1))
elif after not in text:
    raise RuntimeError('Pinned compiler attribute was not found')
patch = root / 'buildscripts/patches/mbedtls/0001-clang-aes-target.patch'
patch.parent.mkdir(parents=True, exist_ok=True)
header = ('Backport: https://github.com/Mbed-TLS/mbedtls/pull/7878\n'
          'Upstream commit: aa4f6219014d863bed51453e5261178adc66be34\n\n')
patch.write_text(header + subprocess.check_output(
    ['git', '-C', str(repo), 'diff', '--', 'library/aesce.c'], text=True))
