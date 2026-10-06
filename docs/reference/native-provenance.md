# Native source provenance

The Android build derives from media-kit's `libmpv-android-video-build` v1.1.7,
commit `fe8c3ac1a91c09aa6fb1deccbc833f1bafa54768`. This repository builds libmpv;
the existing MediaKit Dart API and other platform providers remain separate.

`sources.lock.json` records nine native dependency revisions, the NDK revision,
and hashes of the applied patches and compilation recipes. Its packaged copy
is in `packages/flutter_media_kit/native_sources/`. The package's
`android/native-manifest.json` records both JAR and inner-library hashes.

## Maintained changes

The GLES patch retries a failed context request without optional EGL context
flags while preserving the requested GLES version and original first attempt.
`scripts/test_egl_fallback.py` compiles the actual pinned mpv function with a
rejecting EGL driver and compares original and patched behavior.

The Mbed TLS patch backports the compiler-attribute adjustment from
[Mbed TLS PR 7878](https://github.com/Mbed-TLS/mbedtls/pull/7878), allowing the
selected NDK to compile its ARM64 AES intrinsics. Runtime hardware checks still
guard crypto acceleration. The source kit includes these and the retained
FFmpeg/mpv patches with their exact build inputs.

The JNI helper binaries are retained from upstream v1.1.7 and checksum-verified.
Their Java namespaces and class names are compatibility contracts, so they
continue to use `com.alexmercerind` after the Flutter package was renamed.

## Distribution materials

The Flutter/Java wrapper retains the upstream MIT license. mpv is built with
GPL features disabled, while FFmpeg's version-3 configuration introduces LGPLv3
terms alongside dependency licenses. The entire native distribution is not
MIT-only. See the package [NOTICE.md](../../packages/flutter_media_kit/NOTICE.md)
and [license texts](../../packages/flutter_media_kit/licenses/).

The generated source archive includes pinned upstream trees and submodules,
patches, recipes and instructions for rebuilding/replacing libmpv. It is bundled
in the pub.dev package rather than committed as a large archive in Git. Release
preparation verifies the locked inputs and native binaries before generating it.

Archived upstream Gradle/bundle tooling in [legacy/](../../legacy/README.md)
is outside the supported pipeline. Moving it does not alter the locked recipes
or the native artifact hashes.
