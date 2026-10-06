# Android package publication validation — 2026-10-06

Release: `flutter_media_kit` `1.3.8+ppplayer.egl1`.
Published successfully to https://pub.dev/packages/flutter_media_kit on 2026-10-06.
The registry confirms this version and declares the Android plugin only.

* Flutter 3.47.4 / Dart 3.13.3 on Windows.
* After the user selected `flutter_media_kit`, the renamed example was rebuilt
  and the APK library hashes verified again.
* Runnable Android example resolves the renamed provider directly alongside
  MediaKit and MediaKit Video, without the original native Android provider.
* Example static analysis passes.
* Debug APK build passes for ARM64 and x64. Both libmpv binaries and both retained
  JNI helper binaries in the APK match the packaged SHA-256 manifest.
* APK SHA-256: `8a25af9698bb586471d57a80f7dd781ccf707becd9754fc6235b6bfb5e9e538a`.
* JAR, inner-library and pinned source-lock verification passes. Missing and
  altered JARs were rejected in isolated negative checks.
* Corresponding sources, submodule sources, patches, build recipes and license
  materials are included. Source archive generation was repeated with the same
  checksum: `88fbc9490c4ad5eb5d03b76fd17aa95448a076f4cf6a8c920894513e85fb4a48`.
* Package archive includes the generated source kit and both native JARs;
  compressed publication size is about 76 MB.

The initial consumer build failed because C: ran out of disk space. After space
was made available, the same build succeeded. No global caches were deleted by
this preparation work.

This pass checks compilation and APK packaging. The new example was not run on
an emulator in this pass. Prior playback acceptance used these same native
binaries; the package README and platform audit distinguish emulator playback
from pending physical ARM64 and audible-output checks. Other platform binaries
are absent. The main ppplayer application dependencies remain unchanged.

## Hosted-package consumer verification

A separate consumer app resolved `flutter_media_kit: 1.3.8+ppplayer.egl1` from
pub.dev without a local path or dependency override. Static analysis and its
ARM64/x64 debug APK build pass. The downloaded source archive, source lock, both
JARs, and all four native libraries pass checksum verification. The consumer
APK's four native libraries match the downloaded package manifest.

Hosted-consumer APK SHA-256: `8202d334ffd9db6f141c1c4a5b6773e4fbde4dbbbd9de2e45ee22b9c5801f56b`.
This verifies the published package's contents and builds, not a new emulator
playback or physical-device acceptance run.
