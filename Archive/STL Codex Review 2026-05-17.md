# STL Codex Review 2026-05-17

Reviewed: 2026-05-17 02:04

1/ General architecture:
- The repo mixes source scripts and generated STL/3MF artifacts in the same folders.
- A clearer split between `src/`, `models/`, `outputs/`, and `archive/` would make it much easier to review and regenerate work.
- Each model script should state its parameters, dependencies, and generated outputs.

2/ UI:
- No UI is present, which is fine for geometry scripts.
- The practical interface is file names and generated artifacts; those should be predictable and documented.
- Preview images or thumbnails would help identify outputs without opening CAD/slicer tools.

3/ UX:
- Users need to know which script produced which file and whether artifacts are current.
- A one-command regenerate path would reduce confusion and prevent stale `.prev` files from becoming accidental references.
- Output dimensions and units should be explicit.

4/ Testing:
- Add smoke checks that regenerate one tiny model and verify non-empty STL/3MF output.
- Add geometry assertions for bounding boxes and expected component counts.
- Add a script to compare generated artifact timestamps or hashes against source scripts.

5/ Everything else:
- The repo is ahead of origin, so GitHub handoff is incomplete.
- `.prev` exports need a policy: release artifact, backup, or disposable.
- Large binary artifacts may eventually need Git LFS or release assets.

6/ My suggetions:
1. Add a README mapping each script to generated STL/3MF outputs and units.
2. Move generated artifacts into `outputs/` or `models/` and keep source scripts separate.
3. Add a smoke script that regenerates one small model and verifies output files.
4. Add bounding-box/non-empty geometry checks for generated meshes.
5. Decide the retention policy for `.prev` exports and large binary artifacts.
