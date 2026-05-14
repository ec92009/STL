# STL Codex Review 2026-05-12

Reviewed: 2026-05-12

1/ General architecture

- STL appears to be a collection of Python-generated geometry scripts plus generated `.stl` and `.3mf` outputs.
- There is no visible README or package config, so intent, dependencies, and regeneration workflow are not discoverable.
- `house/house.py` is large for a geometry script and likely mixes model parameters, mesh construction, and export behavior.
- Generated artifacts should be clearly distinguished from source scripts and stable reference outputs.

2/ UI

- There is no app UI, but the user interface is effectively the script parameters and generated files.
- Add a simple CLI or documented parameter block for common model variants.
- Consider generating preview images alongside STL/3MF outputs so reviewers can inspect changes without opening CAD/slicer tools.

3/ UX

- The current workflow is hard to infer: users need to know which script to run, what it generates, and which outputs are canonical.
- If previous outputs are retained as backups, document the naming pattern and cleanup policy.
- A single `make`/script command for regeneration would improve confidence.

4/ Testing

- No tests were visible.
- Add geometry smoke tests that verify scripts run, output files are created, meshes are non-empty, and dimensions stay within expected bounds.
- If models have known dimensions, assert bounding boxes and manifold/watertight checks where tooling allows.
- Keep one or two golden reference outputs, but avoid committing every generated experiment.

5/ Everything else

- Add a README before adding more models; otherwise this repo will become an unmaintainable artifact dump.
- Decide whether both `house/` and `torus_stl/` are active or whether one is a historical experiment.
- Add `.gitignore` rules for temporary exports while preserving intentional release/reference artifacts.

6/ My suggetions:

1. Add a README explaining purpose, dependencies, active model folders, and regeneration commands.
2. Create a `scripts/build_all.py` or similar command that regenerates canonical STL/3MF outputs.
3. Split `house/house.py` into parameters, geometry builders, and export helpers.
4. Add smoke tests for script execution, output existence, non-empty meshes, and expected dimensions.
5. Define which generated files are canonical references and ignore temporary or timestamped experiments.
6. Add preview image generation for each canonical model.
