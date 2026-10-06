# Earlier Android emulator acceptance

This records the acceptance summary previously kept in the repository README.
It is historical evidence, not a new test run caused by the folder reorganization.

On 2026-10-05, ARM64 and x64 native builds passed packaging checks. The isolated
ppplayer preview passed 107 playback regression tests and Android 15/16 debug
emulator acceptance: three local-video/YouTube round trips, Home, 20 seconds
with the screen off, system pause/play and activity restoration.

Both emulator logs showed the EGL retry; the Android 16 emulator uses 16 KiB
pages. Debug x64 and release ARM64/x64 APK libraries matched the built artifact
hashes. The standard release APK installed and initialized MediaKit on Android
16 before its first-run permission request. A separate Android 16 release
playback probe also passed, as recorded in the platform audit.

The detailed preview logs belong to the separate ppplayer/webview validation
workspace and are not newly copied into this repository. The newer
[publication record](publication-2026-10-06.md) independently verifies that the
published JARs contain those native binaries.

These automated checks measured progress, controls and lifecycle. They do not
verify audible output or physical ARM64 behavior. Android 15 release playback
remains a separate acceptance gate.
