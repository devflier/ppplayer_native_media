"""Prepare a minimal GLES fallback backport against the pinned mpv source."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
repo = ROOT / 'buildscripts/deps/mpv'
path = repo / 'video/out/opengl/egl_helpers.c'
source = path.read_text()
old = '''        egl_ctx = eglCreateContext(display, config, EGL_NO_CONTEXT, attrs);
    }

    if (!egl_ctx) {
        MP_MSG(ctx, msgl, "Could not create EGL context for %s!\\n", name);'''
new = '''        egl_ctx = eglCreateContext(display, config, EGL_NO_CONTEXT, attrs);
        // Android emulators may reject optional context flags, even when zero.
        // Preserve the GLES version request when retrying without those flags.
        if (!egl_ctx && es) {
            EGLint fallback_attrs[] = {
                EGL_CONTEXT_CLIENT_VERSION, 2,
                EGL_NONE
            };
            MP_VERBOSE(ctx, "Retrying GLES context without optional flags.\\n");
            egl_ctx = eglCreateContext(display, config, EGL_NO_CONTEXT,
                                       fallback_attrs);
        }
    }

    if (!egl_ctx) {
        MP_MSG(ctx, msgl, "Could not create EGL context for %s!\\n", name);'''
if old not in source:
    raise RuntimeError('Pinned EGL source does not match the expected backport site')
path.write_text(source.replace(old, new, 1))
patch = subprocess.check_output(['git', '-C', str(repo), 'diff', '--', 'video/out/opengl/egl_helpers.c'], text=True)
destination = ROOT / 'buildscripts/patches/mpv/0002-egl-optional-flags.patch'
destination.write_text(patch)
print(f'Prepared {destination}')
