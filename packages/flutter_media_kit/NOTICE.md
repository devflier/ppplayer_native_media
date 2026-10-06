# Native distribution notices

The wrapper and retained media-kit Android JNI helper are covered by the
upstream MIT license in LICENSE (Hitesh Kumar Saini, 2021 and later).
The helper is retained from upstream libmpv-android-video-build v1.1.7, commit
fe8c3ac1a91c09aa6fb1deccbc833f1bafa54768. Its binary hashes are recorded in
android/native-manifest.json.

libmpv is built from the source revisions in native_sources/sources.lock.json.
mpv is configured with GPL features disabled. FFmpeg is configured with GPL and
nonfree components disabled and version 3 enabled. The resulting distribution
includes LGPLv3-covered code, alongside permissively licensed dependencies.
The source archive contains the full upstream license notices, including
notices for source files not selected by the build configuration.

| Component | License information |
| --- | --- |
| mpv | LGPL 2.1 or later for the selected configuration; see mpv-Copyright and mpv-LICENSE.LGPL |
| FFmpeg | LGPLv3 for this version-3 configuration; see ffmpeg-LICENSE.md and ffmpeg-COPYING.LGPLv3 |
| dav1d | BSD; see dav1d-COPYING |
| FreeType | FreeType license; see freetype-LICENSE.TXT and freetype-docs-FTL.TXT |
| FriBidi | LGPL; see fribidi-COPYING |
| HarfBuzz | See harfbuzz-COPYING and individual source notices |
| libass | ISC; see libass-COPYING |
| libxml2 | MIT; see libxml2-Copyright |
| Mbed TLS | Apache 2.0; see mbedtls-LICENSE |

Portions of this software are copyright the FreeType Project.
This software is based in part on the work of the Independent JPEG Group.

Complete corresponding native sources, modifications and compilation recipes
are supplied in native_sources/corresponding-source.tar.gz. Preserve these
materials and the applicable license texts when redistributing. The source kit
documents rebuilding libmpv so applications can permit library replacement.
