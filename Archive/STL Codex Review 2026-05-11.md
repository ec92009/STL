# STL Codex Review 2026-05-11

Review time: 2026-05-11 02:05 CEST.

1/ General architecture

- The repo is a small 3D geometry workspace with Python generators and committed STL/3MF outputs.
- Source, generated artifacts, and previous outputs are mixed together. That is workable for experiments but makes it hard to know what should be edited.
- Establish a convention such as `src/`, `models/`, `exports/`, and `archive/` if the project continues.

2/ UI

- No app UI was found. The user-facing surface is the generated geometry.
- If these are meant for repeat use, add rendered preview images or a small catalog page so outputs can be inspected without opening CAD/slicer tools.

3/ UX

- The current workflow is implicit: run Python scripts and inspect generated STL/3MF files.
- Add one command per model or a README table describing what each script generates, required dependencies, and where outputs land.
- Include print assumptions such as scale, units, orientation, material, and slicer notes.

4/ Testing

- No tests were found.
- Add basic geometry validation: files generate without error, meshes are non-empty, dimensions are within expected bounds, and exported files exist.
- If mesh libraries are used, add watertight/manifold checks where practical.

5/ Everything else

- The repo lacks a README in the scan. That makes future handoff difficult.
- Generated `.prev` files should be intentionally archived or ignored if they are only scratch backups.

6/ My suggetions:

1. Add a README explaining each model, generation command, and output file.
2. Separate source scripts from generated STL/3MF exports.
3. Add a smoke script that regenerates all models into a temporary output folder.
4. Add dimension/manifold checks for generated meshes.
5. Add preview PNGs or thumbnails for each current model.
