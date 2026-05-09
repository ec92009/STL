# STL Codex Review 2026-05-08

Generated: 2026-05-08 00:00 Europe/Madrid

1/ General architecture

- The repo looks like a collection of CAD/STL generation experiments rather than a packaged tool. That is acceptable, but each model family needs a README explaining source script, generated outputs, parameters, and regeneration command.
- Generated `.stl` and `.3mf` files live beside scripts. For repeatability, separate source models from generated artifacts or add a manifest that states which binary outputs are canonical.

2/ UI

- There is no UI. If this remains script-driven, the "UI" is the command surface: use named parameters, clear output paths, and preview-generation commands.
- Consider adding thumbnail renders for generated parts so a reviewer can inspect outputs without opening CAD/slicer tools.

3/ UX

- A new user cannot tell which script to run first or which generated file is current. Add a top-level README with a short catalog of models and exact commands.
- Preserve prior output versions only when they are meaningful; timestamped `.prev` files need explanation or cleanup rules.

4/ Testing

- There are no visible tests. Add geometry sanity checks: output file exists, bounding box dimensions are plausible, mesh is watertight/manifold where expected, and units are documented.
- A regeneration test for one small model would catch broken CAD dependencies.

5/ Everything else

- Binary model files can bloat Git quickly. Decide whether outputs belong in Git, Git LFS, release artifacts, or ignored local build folders.
- Add license/usage notes if the models are intended for reuse or publication.

6/ My suggetions:

1. Add a top-level README catalog with each model, source script, output files, and regeneration command.
2. Separate source scripts from generated STL/3MF outputs or add a manifest for canonical artifacts.
3. Add mesh sanity checks for bounding boxes, watertightness, and file generation.
4. Add preview thumbnails for current generated parts.
5. Decide a Git/LFS/release policy for binary CAD outputs.
