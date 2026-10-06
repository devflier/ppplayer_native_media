# Publish flutter_media_kit

The package is published from `packages/flutter_media_kit`. The first release,
`1.3.8+ppplayer.egl1`, is already on pub.dev. A folder or documentation
reorganization does not modify that immutable release.

## Prepare a new release

Choose a new package version and add its changes to the package changelog.
Preserve the JNI Java package/class names; the retained native helper relies on
those signatures. For native changes, complete the [build checks](building-android.md)
and required playback acceptance before promoting new binaries.

From the repository root:

```sh
python3 scripts/prepare_pub_package.py
python3 scripts/prepare_pub_package.py --verify-only
cd packages/flutter_media_kit/example
flutter pub get
flutter analyze
flutter build apk --debug --target-platform android-arm64,android-x64
```

Back at the repository root:

```sh
python3 scripts/verify_apk.py packages/flutter_media_kit/example/build/app/outputs/flutter-apk/app-debug.apk --package packages/flutter_media_kit
```

The preparation script fetches only the pinned source trees, including their
pinned submodules. It bundles sources, patches, recipes and license materials
without rebuilding the tested JARs or downloading an NDK. To reuse a native-build
cache, pass `--sources-root /path/to/buildscripts/deps`.

The generated `native_sources/corresponding-source.tar.gz` is ignored by Git;
the package's `.pubignore` explicitly includes it in the upload. Its checksum
is recorded in `native_sources/archive.json`. Commit the reviewed release
metadata, source lock, notices and binary changes before the final dry run:

```sh
cd packages/flutter_media_kit
flutter pub get
flutter pub publish --dry-run
```

Verify that the output includes both Android JARs, license materials, source
archive and example, with zero warnings. Do not republish an existing version.

## Manual publication

Run `flutter pub publish` from the package folder using the maintainer's pub.dev
account. Once available, resolve that exact hosted version from a separate app
without path overrides. Analyze, build both Android targets, and compare the
consumer APK's libraries with the downloaded manifest. Record results under
`docs/validation/`.

## GitHub automation

The workflow in `.github/workflows/publish.yml` uses matching `v{{version}}`
tags, verifies the tag/package version, prepares sources, builds the example,
checks the shipped native hashes, and publishes with GitHub OIDC. Enable and
verify this repository/tag pattern in the package's pub.dev Admin settings
before relying on tag publication. This repository alone cannot establish that
the account-side trust configuration is enabled.

Do not push the already manually published version's tag as a publication
request: the workflow would try to publish the same version again. Configure
automation for the next new release. A verified publisher transfer is managed
separately in pub.dev Admin.
