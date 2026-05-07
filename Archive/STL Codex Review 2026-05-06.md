# STL Codex Review 2026-05-06

Timestamp: 2026-05-06 02:02 CEST

## 1/ General architecture

- The repo is currently a collection of geometry scripts plus generated STL/3MF outputs.
- Separate source scripts from generated artifacts so it is clear which files are editable design logic.
- Add reusable geometry helpers for repeated house/body/roof patterns instead of duplicating script variants.
- Decide whether the repo is a library of parametric models or a gallery of finished exports.

## 2/ UI

- There is no app UI, but the developer interface should be clearer: one command per model to regenerate outputs.
- Add preview images for each model if this repo is meant to be browsed by humans.
- Use consistent naming so `house`, `torus_stl`, and future models read as a catalog.

## 3/ UX

- Provide a "regenerate all" workflow that writes outputs to a predictable build directory.
- Add instructions for required CAD/mesh dependencies and how to view outputs.
- Keep previous exports only when they are intentionally versioned examples.

## 4/ Testing

- Add smoke tests that run each parametric script and assert output files are created.
- Add mesh sanity checks where possible: non-empty mesh, positive bounds, and expected object count.
- Avoid binary fixture comparison unless there is a stable export format.

## 5/ Everything else

- Add a README; right now the repo is hard to understand from the file tree alone.
- Add `.gitignore` patterns or a `generated/` convention for exports.
- Consider storing screenshots instead of multiple historical binary exports.

## 6/ My suggetions:

1. Add a README defining repo purpose, dependencies, and regenerate commands.
2. Move generated STL/3MF files into a consistent output directory.
3. Extract shared geometry helpers for house/body/roof scripts.
4. Add smoke tests for each model generation script.
5. Add preview images or a catalog index if humans are expected to browse outputs.
