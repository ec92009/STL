# STL Codex Review 2026-05-19

Timestamp: 2026-05-19 02:02:56 CEST

1/ General architecture

- The repo is mostly geometry scripts plus generated STL/3MF outputs.
- It needs a README that explains whether it is a scratchpad, fixture library, or reusable model-generation project.
- Separate source scripts from generated exports so regeneration is obvious.

2/ UI

- There is no app UI; the user interface is file organization and script naming.
- Generated model names should communicate dimensions/version/source script.
- Preview images or simple render snapshots would make review easier than opening CAD files manually.

3/ UX

- A future operator needs exact commands to regenerate each model.
- Keep old `.prev` files only if they serve a documented comparison purpose.
- Put outputs in predictable `out/` folders rather than mixed with source scripts.

4/ Testing

- Add basic mesh validation: file exists, non-empty, manifold/expected triangle count where feasible.
- Add script smoke tests that regenerate into a temporary directory.
- Keep binary fixture size low.

5/everything else

- No top-level README was visible in the inventory.
- Versioning and dependency expectations are not documented.
- If this is archival, state that and stop expanding it.

6/ My suggetions:

1. Add a top-level README describing purpose, dependencies, and regeneration commands.
2. Move generated STL/3MF outputs under `out/` or per-model output folders.
3. Add smoke tests that regenerate models into a temp directory.
4. Add lightweight mesh validation for generated files.
5. Remove or document `.prev` artifacts.
