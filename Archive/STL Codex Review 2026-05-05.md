# STL Codex Review 2026-05-05

Generated: 2026-05-05 10:36:54 CEST

1/ General architecture

- STL is currently a collection of geometry scripts and generated `.stl`/`.3mf` outputs, mostly around house/torus examples. It reads like a modeling scratchpad rather than a reusable project.
- Separate source scripts from generated mesh artifacts. Keep `models/` or `outputs/` for intentional generated files, and document which outputs are canonical.
- Add dependency metadata; there is no README or config explaining how to regenerate meshes.

2/ UI

- There is no UI. For this kind of repo, the useful interface is a CLI: list models, build one model, export STL/3MF, and optionally open the result.
- Add preview images for each model so the GitHub repo is understandable without downloading mesh files.

3/ UX

- A user should be able to run one command from a fresh clone and reproduce the house or torus files.
- Add naming conventions for versioned previous outputs. The current `.prev` timestamp files are understandable locally but noisy in version control.

4/ Testing

- Add smoke tests that run each generator into a temp directory and assert output files exist and are non-empty.
- If geometry libraries expose mesh checks, validate manifoldness or at least triangle count bounds.

5/ Everything else

- Add `.gitignore` rules for temporary generated exports while explicitly tracking known-good releases.
- Consider using a `Makefile` or `uv` project if the scripts depend on non-stdlib packages.

6/ My suggetions:

1. Add README regeneration commands and dependency notes.
2. Move generated meshes into `outputs/` with a clear canonical/latest policy.
3. Add a `build_all.py` or `make all` workflow.
4. Add smoke tests for all model generators.
5. Add preview PNGs for GitHub browsing.
