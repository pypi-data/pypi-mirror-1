Supported options
=================

patch-binary
    Path to the ``patch`` program. Defaults to 'patch' which should
    work on any system that has the ``patch`` program available in the
    system ``PATH``.

patch-options
    Options passed to the ``patch`` program. Defaults to ``-p0``.

patches
    List of patch directories to be searched and then applied to the
    extracted source. Each file should be given on a separate
    line. The patch files prefix (up to the first '-') will be used to
    match the patch file to the target directory. Accepts globbing.

target
    List of directories to be searched for names matching the found
    patch files. For each matching directory/patch combination, the
    patch will be applied in place.
