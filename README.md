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

The Flutter plugin is named `flutter_media_kit`. Both
validated Android JARs are committed and distributed with the package. Gradle
checks their bundled SHA-256 manifest; it never downloads fallback binaries.
See the [package README](packages/media_kit_libs_android_video/README.md) for
installation and the [platform audit](docs/platform-support.md) for coverage.

Depend directly on the new package alongside `media_kit` and `media_kit_video`.
Remove the original Android provider and the `media_kit_libs_video` umbrella,
which brings it in transitively. The old-name override shown in earlier revisions
is invalid: pub requires dependency keys to match the package's declared name.
For local development, the override key must be
`flutter_media_kit`.

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

## Publication

The package includes upstream license notices, the binary/source lock manifest,
and a complete corresponding source archive with patches and build recipes.
Prepare that archive and verify the committed JARs before any publication:

```sh
python3 scripts/prepare_pub_package.py
python3 scripts/prepare_pub_package.py --verify-only
cd packages/media_kit_libs_android_video
flutter pub get
flutter pub publish --dry-run
```

The preparation script fetches pinned sources without downloading the NDK or
rebuilding the already validated JARs. On WSL, `--sources-root` can select an
existing pinned dependency cache. The generated source archive is excluded from
Git but included in the pub.dev upload by the package's `.pubignore`.

The first release must be published manually with `flutter pub publish`.
After the package exists, configure pub.dev Admin automated publishing for this
repository and matching `v{{version}}` tags. The publishing workflow validates
the tag, prepares the source kit and verifies the package before using GitHub
OIDC. A verified publisher can be selected by transferring the new package in
pub.dev Admin after its first publication.

The upstream broad bundle/release scripts are retained for reference; use the
focused scripts above. This repository owns Android binaries only. Windows,
Linux, macOS, iOS and web require separate providers. Physical ARM64 playback,
audible output, and Android 15 release playback remain acceptance work; see the
platform audit. No main app dependency is changed by preparing this release.
