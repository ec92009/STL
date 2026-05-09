# STL Codex Review 2026-05-09

Generated: 2026-05-09 00:00 Europe/Madrid

1/ General architecture

- STL is a collection of CAD generation experiments rather than a packaged tool. That is fine, but each model family needs a catalog entry with source script, parameters, generated outputs, and regeneration command.
- Generated `.stl` and `.3mf` binaries live beside source scripts. Add a manifest or separate build-output policy so canonical artifacts are clear.

2/ UI

- There is no UI; the command surface is the interface. Scripts should expose named parameters, deterministic output paths, and clear summaries.
- Add preview thumbnails or rendered screenshots so generated parts can be reviewed without opening slicer/CAD tools.

3/ UX

- A new user cannot tell which script to run first or which output is current. A top-level README catalog would solve most of that.
- Timestamped previous files need either cleanup rules or a stated reason to stay in Git.

4/ Testing

- No tests are visible. Add geometry sanity checks for file generation, bounding boxes, units, and watertight/manifold expectations.
- A regeneration smoke test for one small model would catch broken CAD dependencies.

5/ Everything else

- Binary CAD files can bloat the repo. Decide whether they belong in Git, Git LFS, releases, or ignored build folders.
- Add license/usage notes if models are intended for reuse.

6/ My suggetions:

1. Add a README catalog for each model, source script, output, and regeneration command.
2. Add a manifest identifying canonical generated STL/3MF artifacts.
3. Add mesh sanity checks for output existence, dimensions, units, and manifoldness.
4. Add preview thumbnails for current generated parts.
5. Decide a Git/LFS/release policy for binary CAD outputs.
