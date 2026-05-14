# STL Codex Review 2026-05-13

Reviewed: 2026-05-13

1/ General architecture

- STL is a collection of Python-generated geometry scripts plus generated `.stl` and `.3mf` artifacts.
- There is still no visible README or package config, so purpose, dependencies, and regeneration workflow are hard to discover.
- `house/house.py` is large for a geometry script and likely mixes parameters, mesh construction, and export behavior.
- Generated artifacts, timestamped backups, and canonical outputs need a clear tracking policy.

2/ UI

- There is no app UI; the user interface is the script parameters and generated files.
- Add a documented parameter block or small CLI for common model variants.
- Preview images would make reviews much easier because users should not need CAD/slicer tools just to inspect output changes.
- If both `house/` and `torus_stl/` are active, each needs a clear entrypoint.

3/ UX

- The workflow is currently inferential: users need to know which script to run, what it generates, and which outputs are canonical.
- Backup file naming should be documented or cleaned so historical exports do not look like active deliverables.
- A single build command would make regeneration safer and more repeatable.
- Output dimensions and units should be explicit.

4/ Testing

- No tests were visible.
- Add smoke tests that run generation scripts, confirm output files exist, and check meshes are non-empty.
- If dimensions are known, assert bounding boxes and simple manifold/watertight checks where tooling permits.
- Keep one or two golden reference outputs rather than every experiment.

5/ Everything else

- Local `.DS_Store` files are visible and should be ignored/cleaned if not intentionally tracked.
- Add a README before adding more model folders.
- Decide whether generated `.3mf` and `.stl` files are source-of-truth deliverables or reproducible build artifacts.

6/ My suggetions:

1. Add a README explaining purpose, dependencies, active model folders, units, and regeneration commands.
2. Create a `scripts/build_all.py` or similar command for canonical STL/3MF regeneration.
3. Split `house/house.py` into parameters, geometry builders, and export helpers.
4. Add smoke tests for script execution, output existence, non-empty meshes, and expected dimensions.
5. Define which generated files are canonical references and ignore temporary/timestamped experiments.
6. Generate preview images for canonical models.
