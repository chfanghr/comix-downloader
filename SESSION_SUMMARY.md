# Session Summary

This document records the packaging and downloader changes made during the
October 2026 maintenance session.

## Nix Packaging

- Added a reproducible `flake.nix` using `flake-parts` and `uv2nix`.
- Added `pyproject.toml` and a locked Python dependency set in `uv.lock`.
- Added `flake.lock` for pinned Nix inputs.
- The default package is the CLI and is available with:

  ```sh
  nix run . -- --help
  ```

- The packaged executable is available after building with:

  ```sh
  nix build .#default
  ./result/bin/comix-downloader --help
  ```

- Chromium is included at runtime for `nodriver`.
- The GUI is intentionally excluded from the Nix package.
- The development shell is available with `nix develop`.

## Cookie Persistence

Cookies are stored in the user configuration directory rather than the source
tree or Nix store:

```text
$XDG_CONFIG_HOME/comix-downloader/cf_cookies.dat
```

The current working directory's `cf_cookies.dat` remains a legacy fallback.
Files bundled in the source tree are never loaded as cookies, because they may
be inside `/nix/store` and are read-only.

## Comix API Compatibility

The Comix site changed its JavaScript bundle layout. The resolver now supports
both the older `env-*.js` bundles and current `apicore-*.js` bundles.

Current API methods are supported alongside the old names:

| Operation | Older name | Current name |
| --- | --- | --- |
| Manga list | `list` | `ks` |
| Trending | `top` | `XU` |
| Chapters | `chapters` | `uw` |

The resolver first checks already-loaded browser resources and then falls back
to scanning module imports.

## CDN Image Downloads

The image CDNs return `403 Forbidden` when requests include:

```text
Referer: https://comix.to/
```

The HTTP session now adds the `Referer` and Comix cookies only for Comix hosts.
CDN requests receive neither. This was based on upstream PR #29:

<https://github.com/Yui007/comix-downloader/pull/29>

## Output Directory

The default output directory is now `.`. Relative paths resolve from the
current working directory, not the package source directory.

Legacy configuration files inside `/nix/store` are not migrated.

## Resumable Downloads

Successful pages are persisted immediately while a chapter downloads. Progress
is stored under:

```text
<download-path>/<safe-manga-title>/.comix-progress/<chapter-id>-<chapter-folder>/
```

The manifest is `progress.json` and is keyed by the comic ID:

```json
{
  "1nkd": {
    "version": 1,
    "total": 44,
    "completed": [1, 2, 3]
  }
}
```

Cached page bytes are stored beside the manifest as zero-padded `.bin` files.
Interrupted runs validate and reuse completed pages, downloading only missing
pages. Progress state is removed after successful chapter completion.

## Verification

The packaged downloader was tested against:

```text
https://comix.to/title/1nkd
```

The final run downloaded all three chapter-1 variants successfully, including
44, 44, and 40 pages, and created CBZ files.

Useful checks:

```sh
nix flake check --no-build
nix develop --command pytest -q
```

The full suite has one pre-existing failure in
`tests/test_nodriver_compat.py::NodriverCompatTests::test_non_target_modules_are_not_intercepted`.
The remaining tests pass and GUI tests are skipped when PyQt6 is absent.

## Git History

Work was developed and pushed on branch `nixified`:

- `f588bb4 feat: package CLI with Nix flake`
- `67645ea fix: store cookies outside Nix store`
- `1026745 fix: download CDN images without referer`
- `6c2c69e fix: default downloads to current directory`
- `06c095f feat: resume interrupted downloads`

The branch tracks `origin/nixified` at:

```text
git@github.com:chfanghr/comix-downloader.git
```
