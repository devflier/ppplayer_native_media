"""Compile the pinned mpv function against a driver that rejects optional EGL flags."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
repo = ROOT / 'buildscripts/deps/mpv'
relative = 'video/out/opengl/egl_helpers.c'

def function(source):
    start = source.index('static bool create_context(')
    body = source.index('{', start)
    depth = 0
    for index in range(body, len(source)):
        if source[index] == '{':
            depth += 1
        elif source[index] == '}':
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise RuntimeError('Cannot extract the native EGL function')

prefix = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef int EGLint;
typedef int EGLenum;
typedef int EGLDisplay;
typedef int EGLConfig;
typedef void *EGLContext;
enum { EGL_OPENGL_API=1, EGL_OPENGL_ES_API, EGL_OPENGL_BIT, EGL_OPENGL_ES2_BIT,
       EGL_SURFACE_TYPE, EGL_WINDOW_BIT, EGL_RED_SIZE, EGL_GREEN_SIZE,
       EGL_BLUE_SIZE, EGL_ALPHA_SIZE, EGL_RENDERABLE_TYPE,
       EGL_CONTEXT_MAJOR_VERSION, EGL_CONTEXT_MINOR_VERSION,
       EGL_CONTEXT_OPENGL_PROFILE_MASK, EGL_CONTEXT_OPENGL_CORE_PROFILE_BIT,
       EGL_CONTEXT_OPENGL_DEBUG_BIT_KHR,
       EGL_CONTEXT_CLIENT_VERSION=0x3098, EGL_CONTEXT_FLAGS_KHR=0x30fc,
       EGL_NONE=0x3038 };
#define EGL_NO_CONTEXT NULL
enum { MSGL_V, MSGL_FATAL, MSGL_TRACE, MSGL_DEBUG };
#define MP_VERBOSE(ctx, ...) ((void)(ctx), printf(__VA_ARGS__))
#define MP_DBG(ctx, ...) ((void)(ctx), printf(__VA_ARGS__))
#define MP_MSG(ctx, level, ...) ((void)(ctx), (void)(level), printf(__VA_ARGS__))
#define MPGL_VER_GET_MAJOR(v) ((v)/100)
#define MPGL_VER_GET_MINOR(v) (((v)%100)/10)
#define talloc_array(ctx, type, count) ((type *)calloc(count, sizeof(type)))
#define talloc_free(ptr) free(ptr)
struct ra_ctx { struct {bool probing, want_alpha, debug;} opts; void *log; };
struct mpegl_cb {int (*refine_config)(void *, EGLConfig *, int); void *user_data;};
static const int mpgl_min_required_gl_versions[] = {0};
static int calls, reject_flags, reject_all, configs_available=1;
static void dump_egl_config(void *log, int level, EGLDisplay display, EGLConfig config) {}
static int eglBindAPI(EGLenum api) {return 1;}
static int eglChooseConfig(EGLDisplay display, const EGLint *attrs,
                           EGLConfig *configs, int count, int *total) {
    *total = configs_available;
    if (configs && count > 0) configs[0] = 77;
    return 1;
}
static EGLContext eglCreateContext(EGLDisplay display, EGLConfig config,
                                    EGLContext shared, const EGLint *attrs) {
    calls++;
    bool flags = false, gles2 = false;
    for (int i=0; attrs[i] != EGL_NONE; i+=2) {
        flags |= attrs[i] == EGL_CONTEXT_FLAGS_KHR;
        gles2 |= attrs[i] == EGL_CONTEXT_CLIENT_VERSION && attrs[i+1] == 2;
    }
    assert(gles2);
    if (reject_all || (reject_flags && flags)) return NULL;
    return (EGLContext)0x1234;
}
'''

main = r'''
int main(int argc, char **argv) {
    struct ra_ctx ctx = {0};
    struct mpegl_cb cb = {0};
    EGLContext out = NULL;
    EGLConfig config = 0;
    reject_flags = 1;
    bool success = create_context(&ctx, 1, true, cb, &out, &config);
    if (argc > 1 && strcmp(argv[1], "original") == 0) {
        assert(!success && calls == 1);
        puts("Original pinned function reproduces flag-rejection failure.");
        return 0;
    }
    assert(success && calls == 2 && out != NULL && config == 77);
    calls = 0; reject_flags = 0;
    assert(create_context(&ctx, 1, true, cb, &out, &config) && calls == 1);
    calls = 0; reject_all = 1;
    assert(!create_context(&ctx, 1, true, cb, &out, &config) && calls == 2);
    calls = 0; reject_all = 0; configs_available = 0;
    assert(!create_context(&ctx, 1, true, cb, &out, &config) && calls == 0);
    puts("Patched native function passes fallback, supported-driver, terminal-failure and missing-config cases.");
    return 0;
}
'''

work = ROOT / '.work/egl-test'
work.mkdir(parents=True, exist_ok=True)
original = subprocess.check_output(['git', '-C', str(repo), 'show', 'HEAD:' + relative], text=True)
patched = (repo / relative).read_text()
for name, source in (('original', original), ('patched', patched)):
    file = work / (name + '.c')
    binary = work / name
    file.write_text(prefix + function(source) + main)
    subprocess.run(['cc', '-std=c11', str(file), '-o', str(binary)], check=True)
    subprocess.run([str(binary)] + (['original'] if name == 'original' else []), check=True)
