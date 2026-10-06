# Android package publication validation — 2026-10-06

Candidate: `ppplayer_media_kit_libs_android_video` `1.3.8+ppplayer.egl1`.
This report records preparation checks; it does not assert pub.dev publication.

* Flutter 3.47.4 / Dart 3.13.3 on Windows.
* Runnable Android example resolves the renamed provider directly alongside
  MediaKit and MediaKit Video, without the original native Android provider.
* Example static analysis passes.
* Debug APK build passes for ARM64 and x64. Both libmpv binaries and both retained
  JNI helper binaries in the APK match the packaged SHA-256 manifest.
* APK SHA-256: `ae638cc2f09503e5be92deac94508bf75af62f873bb0c834774f45c4382a0fc6`.
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
