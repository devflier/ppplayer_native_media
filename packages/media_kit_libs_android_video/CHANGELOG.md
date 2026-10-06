## 1.3.8+ppplayer.egl1

* Initial ppplayer Android native-library release, derived from media-kit Android
  video build v1.1.7 with pinned dependencies.
* Retry GLES context creation without optional EGL flags when the first request
  fails; preserve the requested GLES version.
* Backport the Mbed TLS ARM64 AES compiler-attribute fix.
* Include ARM64 and x64 binaries with verified 16 KiB ELF alignment, artifact
  checksums, corresponding native sources, patches and license notices.
* Preserve the existing MediaKit JNI helper and Dart playback APIs.
* Other platforms and 32-bit Android architectures are not included.
