# Repository reorganization validation - 2026-10-06

The Flutter package moved to `packages/flutter_media_kit`. Documentation now
has guides, reference material and dated validation records. Unsupported upstream
Gradle/bundle tooling is archived under `legacy/`; active native recipes stay in
`buildscripts/`.

* Windows Flutter 3.47.4 / Dart 3.13.3.
* Example dependencies resolve from the relocated package, and static analysis
  passes.
* The ARM64/x64 debug APK builds from the new folder. Both libmpv and JNI helper
  libraries for both architectures match the package manifest.
* APK SHA-256: `5de735eafc7154a628637e91277bfdcaa134826a03fa25fb16e15726202ef653`.
* All locked native recipe and patch hashes remain unchanged.
* JAR, inner-library, source lock and corresponding-source archive verification
  pass. Archive SHA-256 remains `88fbc9490c4ad5eb5d03b76fd17aa95448a076f4cf6a8c920894513e85fb4a48`.
* Local documentation links and publishing workflow directories were checked.

The native binaries and package version are unchanged. No new emulator playback,
physical-device acceptance or pub.dev publication was performed for this
reorganization. The [existing release validation](publication-2026-10-06.md)
records the published package's checks.

Windows retained a lock on the old local build-cache folder. Only tracked package
files were moved, and the generated source archive was preserved in the new
package folder. Remaining old local caches are ignored; a fresh Git checkout
contains only the new package layout.
