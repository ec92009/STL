# STL Codex Review 2026-05-14

Review timestamp: 2026-05-14, Europe/Madrid.

1/ General architecture

- The repo is currently a small collection of Python geometry scripts and generated STL/3MF outputs.
- There is no README or project metadata visible, so the purpose and regeneration workflow are not self-documenting.
- Generated artifacts should be separated from source scripts with a clear `generated/` or `outputs/` policy.

2/ UI

- There is no UI surface visible.
- If the repo remains script-only, progress should go into better command output and generated-preview naming.
- If a viewer is planned, choose a lightweight static preview or documented slicer workflow before building a custom UI.

3/ UX

- The primary user task is likely "regenerate this model"; that command should be obvious.
- File naming should identify source script, dimensions/options, and timestamp/version only when useful.
- Old `.prev` artifacts should be pruned or documented so users know which files matter.

4/ Testing

- Add smoke tests that run each generator into a temporary output directory.
- Validate non-empty mesh outputs and basic triangle/bounds sanity.
- Keep golden artifacts small if any are committed.

5/ Everything else

- Large STL/3MF files are present; decide which are canonical examples versus disposable generated outputs.
- Add `.gitignore` rules for local slicer/export experiments.
- Consider common helper functions for repeated house/torus geometry.

6/ My suggetions:

1. Add `README.md` explaining each model, dependencies, and regeneration commands.
2. Move generated STL/3MF files into a documented output folder or mark canonical fixtures.
3. Add generator smoke tests that write to a temporary directory.
4. Add mesh sanity checks for non-empty geometry and expected bounds.
5. Prune or archive `.prev` artifacts after identifying the current canonical outputs.
6. Extract shared geometry/export helpers if more models are added.
