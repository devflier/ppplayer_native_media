# flutter_media_kit - Android native libraries

Android native video and audio libraries for the existing `media_kit` and
`media_kit_video` Dart APIs. This fork builds pinned libmpv sources with an EGL
context fallback and an ARM64 Mbed TLS compiler fix. It retains media-kit's JNI
helper and Java package names for compatibility.

## Supported targets

| Target | Included in this package | Validation |
| --- | --- | --- |
| Android ARM64 (`arm64-v8a`) | Yes, API 21+ | Build, native exports and 16 KiB alignment checked; physical-device playback pending |
| Android x64 (`x86_64`) | Yes, API 21+ | Android 15/16 emulator playback acceptance; Android 16 release playback probe |
| Android ARMv7 / x86 | No | No binaries provided |
| Windows, Linux, macOS, iOS, web | No | Use separate platform providers |

This is an Android native-library provider, not a complete replacement for
MediaKit. Platform badges on another package do not establish support here.
The emulator tests check playback progress, lifecycle and controls; audible
output and physical-device behavior still need validation.

## Installation

Add `media_kit`, `media_kit_video`, and this package to your app:

```yaml
dependencies:
  media_kit: ^1.2.3
  media_kit_video: ^2.0.1
  flutter_media_kit: 1.3.8+ppplayer.egl1
```

Call `MediaKit.ensureInitialized()` before creating players, following the
[MediaKit API documentation](https://pub.dev/packages/media_kit).

Remove `media_kit_libs_android_video` and the `media_kit_libs_video` umbrella
dependency, which pulls in the original Android provider. Including both
providers can cause duplicate Java classes and native libraries. For a
multiplatform app, add the individual native providers for its other platforms.
The renamed package cannot override the original package name: pub requires the
dependency key to match the package's declared name.

For local development, use this key:

```yaml
dependency_overrides:
  flutter_media_kit:
    path: ../ppplayer_native_media/packages/flutter_media_kit
```

The package contains both native JARs. It does not download native binaries
during an app build. Its Gradle verification task rejects missing or altered
JARs using the bundled SHA-256 manifest.

Limit your Android app's `ndk.abiFilters` to `arm64-v8a` and `x86_64`; 32-bit
Android playback is unsupported. For an APK, use
`flutter build apk --target-platform android-arm64,android-x64`.
The runnable `example/` app configures these filters and offers a media URL
field with playback controls.

## Source and licenses

The Flutter/Java wrapper and retained JNI helper use the upstream MIT license.
The native library has additional licenses: mpv is built with GPL features
disabled; FFmpeg is built with `--enable-version3`, with LGPLv3 terms and its
dependency notices. See `NOTICE.md`, `licenses/`, and the complete pinned sources,
patches and build recipes in `native_sources/corresponding-source.tar.gz`.
Do not describe the entire native distribution as MIT-only. Apps distributing
these libraries must preserve their applicable notices and license obligations.

The source archive includes instructions for rebuilding and replacing libmpv.
Native commit pins and artifact hashes are bundled alongside it. Development
and validation details are in the
[repository](https://github.com/devflier/ppplayer_native_media).
