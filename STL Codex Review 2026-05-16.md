# STL Codex Review 2026-05-16

Review timestamp: 2026-05-16 02:03 CEST.

1/ General architecture:
- The repo is a small collection of Python-generated STL/3MF experiments with house and torus outputs.
- It needs a clearer distinction between source scripts, generated artifacts, and retained printable exports.

2/ UI:
- No UI exists, which is fine for a geometry-generation repo.
- If models are meant for reuse, generated preview images or a small README gallery would help users inspect outputs without opening CAD tools.

3/ UX:
- The current workflow is not self-documenting: a new user cannot immediately tell which script regenerates which artifact.
- Add one command per model and document expected output names.

4/ Testing:
- No tests are visible.
- Geometry projects can still test bounding boxes, watertightness where tooling allows, output existence, and deterministic regeneration.

5/ Everything else:
- Large binary exports can be useful, but old `.prev` files should have an explicit retention policy.
- Consider Git LFS or a release artifact strategy if generated models grow.

6/ My suggetions:
1. Add a README that maps each script to its generated STL/3MF outputs.
2. Move generated artifacts into `outputs/` or `models/` so source code is easy to find.
3. Add a smoke script that regenerates one tiny model and verifies the output files exist.
4. Add simple geometry checks for bounding dimensions and non-empty meshes.
5. Decide whether `.prev` exports are archive artifacts, release assets, or disposable backups.
