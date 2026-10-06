# Build Android native libraries

Build on a Linux or WSL Linux filesystem. Required host tools are git, curl,
unzip, Python 3, a C compiler, make, autoconf, automake, libtool, pkg-config,
Meson, Ninja, nasm and CMake. Bootstrap fetches the pinned sources and verified
NDK without requiring a complete Android SDK or administrator access.

From the repository root:

```sh
bash scripts/bootstrap_android.sh
python3 scripts/test_egl_fallback.py
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh x86_64
python3 scripts/package_android.py --abi x86_64
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh arm64
python3 scripts/package_android.py --abi arm64-v8a
```

Build architectures sequentially: dependency builds share generated files.
The source lock records revisions, patch hashes and recipe hashes. Packaging
checks required native exports, 16 KiB ELF alignment and the retained upstream
JNI helper. It produces deterministic JARs and a manifest in `artifacts/`.

## Promote intentionally rebuilt binaries

The plugin ships its own tracked JARs; building into `artifacts/` does not replace
those files automatically. After reviewing a new native build, copy both JARs
to `packages/flutter_media_kit/android/libs/`, its `manifest.json` to
`packages/flutter_media_kit/android/native-manifest.json`, and the corresponding
source lock to `packages/flutter_media_kit/native_sources/sources.lock.json`.
Use LF bytes for the source lock so its recorded checksum remains valid.

Prepare the corresponding source kit using the same pinned dependency cache:

```sh
python3 scripts/prepare_pub_package.py --sources-root buildscripts/deps
python3 scripts/prepare_pub_package.py --verify-only
```

Changes to patches or locked recipes require a deliberate source-lock update,
new binaries, packaging checks and playback acceptance. Do not update a checksum
merely to bypass a failed native-integrity check. The current immutable pub.dev
release stays available; rebuilt libraries require a new package version.

## Check an application APK

```sh
python3 scripts/verify_apk.py /path/to/app.apk --package packages/flutter_media_kit
```

This compares the APK's native libraries with the self-contained package
manifest. Add `--abi x86_64` for an emulator-only APK. Without `--package`, the
verifier uses the build artifacts in `artifacts/`.

Checks of exports, alignment and APK hashes establish build/packaging properties.
They do not replace playback, lifecycle or audible-output acceptance. See
[validation records](../validation/README.md) and
[platform support](../reference/platform-support.md).
