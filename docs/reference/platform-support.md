# Platform support audit

The release package is `flutter_media_kit`. It declares
only an Android Flutter plugin, contains only Android JARs, and has no Windows,
Linux, macOS, iOS or web implementation. Android build-script targets for other
architectures are not evidence that those binaries are shipped.

| Platform | Own native binaries | Acceptance status / next step |
| --- | --- | --- |
| Android x64 | Included | Android 15/16 debug acceptance and Android 16 release playback probe passed; complete Android 15 release playback probe |
| Android ARM64 | Included | Compilation, exports, alignment and APK packaging checked; test playback/lifecycle/audio on a physical device |
| Android ARMv7 / x86 | Absent | Explicitly unsupported by this release |
| Windows | Absent | Continue using the separate upstream MediaKit Windows provider; own build and release validation needed |
| Linux | Absent | Continue using the separate upstream MediaKit Linux provider; WSL native-build work and Linux desktop playback validation needed |
| macOS | Absent | Separate native build/provider and Apple Silicon/Intel validation on macOS needed |
| iOS | Absent | Separate native build/provider, signing and physical-device validation on macOS needed |
| Web | Absent | Separate browser playback backend needed; Android libmpv cannot run in a browser |

The existing MediaKit Dart API supplies the playback interface. This repository
does not yet supply a complete independently maintained multiplatform MediaKit
replacement. Publish the accurately scoped Android provider separately; a later
umbrella package can select verified platform providers once those exist.

Automated playback tests measure progress, seeking, controls and lifecycle.
They do not establish audible output or behavior across all devices/codecs.
