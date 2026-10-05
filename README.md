# ppplayer native media (local candidate)

This repository owns the Android native playback build used by the isolated
ppplayer preview. It starts from media-kit's `libmpv-android-video-build` v1.1.7
(`fe8c3ac1a91c09aa6fb1deccbc833f1bafa54768`). It is not a new playback engine.
The existing MediaKit Dart API and desktop dependencies remain in use.

The first patch retries a failed GLES context request without optional EGL
context flags. It preserves GLES 2 and the original first attempt. A C regression
test compiles the actual pinned mpv function with a rejecting EGL driver and
compares the original and patched behavior. Passing that test alone does not
establish Android runtime compatibility.

The pinned TLS source also includes the small compiler-attribute backport from
[Mbed TLS PR 7878](https://github.com/Mbed-TLS/mbedtls/pull/7878), needed for its
ARM64 AES intrinsics to compile with the selected NDK. Crypto acceleration remains
guarded by the library's runtime hardware check.

## Build on Linux or WSL

Required host tools: git, curl, unzip, Python 3, a C compiler, make, autoconf,
automake, libtool, pkg-config, Meson, Ninja, nasm, and CMake. Build on the Linux
filesystem for reliable performance. The bootstrap downloads and verifies the
pinned NDK and fetches the pinned sources; it does not need a complete Android
SDK or administrator access.

```sh
bash scripts/bootstrap_android.sh
python3 scripts/test_egl_fallback.py
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh x86_64
python3 scripts/package_android.py --abi x86_64
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh arm64
python3 scripts/package_android.py --abi arm64-v8a
```

Build architectures sequentially: some dependencies share generated source
files. `sources.lock.json` records source commits and patch hashes. Packaging
checks native exports and 16 KiB ELF alignment, verifies the upstream JNI helper,
and emits deterministic JARs plus a SHA-256 manifest in `artifacts/`.

The Flutter plugin is `packages/media_kit_libs_android_video`. It intentionally
retains its upstream package name for a private dependency override and has
`publish_to: none`. Its Gradle task requires both locally built architectures,
checks the artifact manifest, and never downloads a fallback native library.
Generated binaries and SDKs are ignored. To use a fresh checkout, build them first.

For an isolated Flutter app next to this repository, add the following override
to its existing `dependency_overrides` mapping and run `flutter pub get`:

```yaml
media_kit_libs_android_video:
  path: ../ppplayer_native_media/packages/media_kit_libs_android_video
```

After an app build, verify the shipped libraries (use `--abi x86_64` for an
emulator-only debug APK; omit it for the two-architecture release APK):

```sh
python3 scripts/verify_apk.py /path/to/app.apk
```

## Ownership and validation

On 2026-10-05, both native architectures built and passed packaging checks.
The isolated ppplayer preview passed 107 playback regression tests and complete
live Android 15/16 emulator acceptance runs: three local-video/YouTube round trips,
Home, 20 seconds with the screen off, system pause/play and activity restoration.
Both logs show the new EGL retry; the Android 16 emulator uses 16 KiB pages.
The debug APK's x86_64 libraries and the release APK's ARM64/x86_64 libraries
match the local artifact hashes. The release APK installs and initializes MediaKit
on Android 16 before its first-run permission request. These automated
tests verify playback progress, not audible output or physical-device behavior.

Keep upstream license notices and source provenance. The retained JNI helper is
from the exact upstream v1.1.7 release; the packaged libmpv is built here. The
root and plugin licenses remain included. Before distribution, preserve license
notices and make the corresponding native sources and patches available.

The upstream broad bundle/release scripts are retained for reference; use the
focused scripts above. CI builds and uploads test artifacts without creating
GitHub releases. No main app dependency should be changed until the native build and
emulator acceptance checks pass. Physical ARM64 device testing and macOS/iOS
validation are separate acceptance gates.
