# Contributing

Read the [repository layout](README.md#repository-layout) and
[documentation index](docs/README.md) first. The package lives in
`packages/flutter_media_kit`; its current native implementation is Android-only.

For package/example changes, run from the repository root:

```sh
python3 scripts/prepare_pub_package.py --verify-only
cd packages/flutter_media_kit/example
flutter pub get
flutter analyze
flutter build apk --debug --target-platform android-arm64,android-x64
```

If the generated corresponding-source archive is absent, prepare it as described
in the [publishing guide](docs/guides/publishing.md) before verification.
Back at the repository root, verify the consumer APK:

```sh
python3 scripts/verify_apk.py packages/flutter_media_kit/example/build/app/outputs/flutter-apk/app-debug.apk --package packages/flutter_media_kit
```

Native changes also require the Linux/WSL build and packaging checks, the actual
EGL regression test, and appropriate runtime acceptance. Preserve JNI namespaces,
source provenance, license texts and pinned build-input hashes. Record meaningful
validation under `docs/validation/`; clearly state any tests not performed.

Folder/documentation changes do not require republishing an immutable version.
When preparing a new release, follow the publishing guide, update its version
and changelog, and verify the exact hosted package after publication.
