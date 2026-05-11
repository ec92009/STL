# STL Codex Review 2026-05-10

Timestamp: 2026-05-10 02:04 CEST

1/ General architecture:

- The repo mixes source scripts and generated 3MF artifacts without a manifest that explains what is canonical. That makes regeneration and review difficult.
- The duplicated `house` and `torus_stl` structures should either share common geometry helpers or be documented as separate experiments.

2/ UI:

- There is no app UI, but the project needs visual review artifacts: thumbnails, dimensions, and model previews for generated parts.
- A simple generated HTML catalog would be enough for inspection.

3/ UX:

- A future maintainer needs to know which command regenerates which model and what units/tolerances are expected.
- Add a "start here" README so this does not require opening each Python file.

4/ Testing:

- There are no mesh sanity checks. Add tests that verify generated files exist, dimensions are plausible, and meshes are manifold when tooling is available.
- Add smoke tests for script execution using temporary output directories.

5/ Everything else:

- Decide whether binary CAD outputs belong in Git, Git LFS, or GitHub releases.
- Keep previous generated versions only when they support comparison; otherwise archive or remove stale binaries.

6/ My suggetions:

1. Add a README catalog mapping each model to source script, output files, units, and regeneration command.
2. Add a manifest identifying canonical generated STL/3MF artifacts.
3. Add mesh sanity checks for output existence, dimensions, units, and manifoldness.
4. Generate preview thumbnails or an HTML catalog for current parts.
5. Decide and document the Git/LFS/release policy for binary CAD outputs.
