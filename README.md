# flutter_media_kit

Android native video and audio libraries for the existing `media_kit` and
`media_kit_video` Dart APIs, maintained for ppplayer.

[Package on pub.dev](https://pub.dev/packages/flutter_media_kit) ·
[Installation](docs/guides/installation.md) ·
[Platform support](docs/reference/platform-support.md) ·
[Documentation](docs/README.md)

The published release is **1.3.8+ppplayer.egl1**. It includes Android ARM64 and
x64 libraries with an EGL context fallback, pinned native sources, license
notices and verified artifact hashes. This release supplies Android native
libraries; the playback API comes from MediaKit. Other platforms require
separate providers.

## Start here

```yaml
dependencies:
  media_kit: ^1.2.3
  media_kit_video: ^2.0.1
  flutter_media_kit: 1.3.8+ppplayer.egl1
```

Remove the original Android provider and the `media_kit_libs_video` umbrella to
avoid duplicate Java classes and native libraries. For other platforms, add
their individual native providers. See the installation guide for initialization,
ABI filters and local development.

A runnable Android example lives in `packages/flutter_media_kit/example`:

```sh
cd packages/flutter_media_kit/example
flutter pub get
flutter run
```

## Repository layout

| Folder / file | Purpose |
| --- | --- |
| `packages/flutter_media_kit/` | Published Flutter plugin, Android JARs, licenses, source kit and example |
| `buildscripts/` | Pinned native compilation recipes and patches |
| `scripts/` | Supported bootstrap, build, packaging, verification and release tools |
| `docs/guides/` | Installation, native builds and publishing |
| `docs/reference/` | Platform coverage and native-source provenance |
| `docs/validation/` | Dated build and publication evidence |
| `legacy/` | Archived upstream Gradle setup and broad bundle scripts |
| `sources.lock.json` | Native revisions and patch/recipe hashes |
| `.github/workflows/` | Native build checks and pub.dev release workflow |

Generated SDKs, dependency checkouts, native build outputs and local logs are
ignored by Git. Validated Android JARs are tracked; the corresponding-source
archive is generated for publication and bundled in the pub.dev download.

## Development and validation

Use the [Android build guide](docs/guides/building-android.md) for Linux or WSL
and the [publishing guide](docs/guides/publishing.md) for releases. See
[CONTRIBUTING.md](CONTRIBUTING.md) for checks required when changing the package.

The published package downloaded, passed static analysis and built an ARM64/x64
consumer APK with all native hashes verified. Earlier Android 15/16 emulator
acceptance used the same native binaries. Physical ARM64 playback, audible
output and additional platforms still need validation. Read the
[validation records](docs/validation/README.md) for the limits of each check.

The wrapper retains the upstream MIT license. The native distribution includes
additional LGPL and dependency licenses; see the package's
[notices](packages/flutter_media_kit/NOTICE.md) and
[native provenance](docs/reference/native-provenance.md).
