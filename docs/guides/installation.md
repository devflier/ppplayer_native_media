# Installation

The current release supplies Android ARM64 (`arm64-v8a`) and x64 (`x86_64`)
native libraries. It uses the existing MediaKit Dart playback API. See
[platform support](../reference/platform-support.md) before selecting targets.

## Published package

```yaml
dependencies:
  media_kit: ^1.2.3
  media_kit_video: ^2.0.1
  flutter_media_kit: 1.3.8+ppplayer.egl1
```

Remove `media_kit_libs_android_video` and the `media_kit_libs_video` umbrella,
which pulls in the original Android provider. Both providers contain the same
Java class names and native-library names, so including both can cause duplicate
definitions. In a multiplatform app, use the individual native providers for
its other platforms alongside this Android provider.

Initialize MediaKit before creating players:

```dart
import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MediaKit.ensureInitialized();
  runApp(const MyApp());
}
```

Use `Player`, `Media`, and `VideoController` from `media_kit` and
`media_kit_video`. This native-only plugin does not export those Dart classes.

## Android architectures

Restrict the app's Android `defaultConfig` to the shipped architectures. For
`android/app/build.gradle.kts`:

```kotlin
defaultConfig {
    ndk {
        abiFilters += listOf("arm64-v8a", "x86_64")
    }
}
```

Build an APK with `flutter build apk --target-platform android-arm64,android-x64`.
32-bit Android binaries are absent. Network media also requires the Android
`INTERNET` permission; the example includes it.

## Example and local development

From the repository root:

```sh
cd packages/flutter_media_kit/example
flutter pub get
flutter run
```

Enter a media URL and press Open to use the playback controls. Choose an ARM64
Android device or x64 emulator. This example configures the ABI filters and
depends on the adjacent local package.

For an app stored next to this repository, retain the `flutter_media_kit`
dependency and add:

```yaml
dependency_overrides:
  flutter_media_kit:
    path: ../ppplayer_native_media/packages/flutter_media_kit
```

Adjust the path to your checkout. The dependency key must match the declared
package name. The old local folder `packages/media_kit_libs_android_video` was
renamed; update existing app overrides and run `flutter pub get`.

Ordinary app builds use the included JARs and do not need the native source
archive or an NDK rebuild. Gradle rejects missing or altered JARs using their
bundled manifest. Native changes follow the [build guide](building-android.md).
