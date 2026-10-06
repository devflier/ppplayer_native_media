# Archived upstream tooling

These files are retained from the upstream Android video build for reference:

* `upstream-gradle/`: the old root Gradle setup and wrapper.
* `upstream-buildscripts/`: broad download, patch and bundle scripts.

They are outside the supported flutter_media_kit build and release pipeline.
The Gradle setup refers to upstream modules/publishing scripts absent from this
checkout. The bundle scripts assume the old working-directory layout and include
cleanup and additional build variants that are not this package's configuration.
Moving them here preserves their contents, not a runnable historical project.

Use the focused tools in `scripts/` and the
[Android build guide](../docs/guides/building-android.md). The active pinned
compilation recipes and patch files remain in `buildscripts/` to preserve the
source-lock hashes and corresponding-source kit.
