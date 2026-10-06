# Corresponding source kit

`corresponding-source.tar.gz` contains the nine pinned dependency source trees,
all tracked native patches, the locked build recipes, and focused build scripts.
`sources.lock.json` identifies the revisions, patch/recipe checksums and NDK.
`archive.json` records the archive SHA-256. JAR and inner shared-library hashes
are in `../android/native-manifest.json`.

Extract into an empty directory on a Linux or WSL Linux filesystem. Install
git, curl, unzip, Python 3, a C compiler, make, autoconf, automake, libtool,
pkg-config, Meson, Ninja, nasm and CMake. Download Android NDK r27d for Linux
from https://dl.google.com/android/repository/android-ndk-r27d-linux.zip;
verify SHA-1 `22105e410cf29afcf163760cc95522b9fb981121`. Place its extracted
contents in `buildscripts/sdk/android-sdk-linux/ndk/27.3.13750724`.

The source trees are pristine; apply the included patches once before building:

```sh
for patch in buildscripts/patches/*/*.patch; do
  dep=$(basename "$(dirname "$patch")")
  (cd "buildscripts/deps/$dep" && patch -p1 < "../../../$patch")
done
cp buildscripts/flavors/default.sh buildscripts/scripts/ffmpeg.sh
chmod +x buildscripts/build.sh buildscripts/scripts/*.sh
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh x86_64
PPPLAYER_BUILD_JOBS=2 bash scripts/build_android.sh arm64
```

Build architectures sequentially. Outputs are
`buildscripts/prefix/<ABI>/lib/libmpv.so`. Packaging strips the library with the
pinned NDK's llvm-strip. Replace `lib/<ABI>/libmpv.so` inside a copy of the
matching Android JAR to use a rebuilt library, retaining the existing JNI helper.
For intentional source modifications, update the artifact manifest/checksums in
your local plugin fork before building your application. The published plugin
rejects accidental changes to its original JARs.

The source-kit bootstrap script is included for reference; the extracted trees
have no Git metadata, so use the instructions above instead of running bootstrap
on top of them. An online repository checkout can use bootstrap to fetch the
exact same sources. Native dependencies do not require regeneration for ordinary
Flutter app builds.
