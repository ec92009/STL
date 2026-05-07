# STL Codex Review 2026-05-07

Reviewed at: 2026-05-07 00:00 Europe/Madrid

1/ General architecture:
- The repo appears to hold geometry scripts rather than a packaged app. `house/house.py` and `torus_stl/house.py` are large and partly duplicative; extract reusable geometry primitives and output helpers.
- Define one entrypoint per model family and keep generated STL/output artifacts separate from source scripts.
- Add parameter objects for dimensions so model variants are reproducible and documented.

2/ UI:
- There is no user-facing UI yet. A small CLI would be enough: choose model, dimensions, output path, and preview/export mode.
- If these scripts are used manually, add readable parameter names and comments at the top of each model file.
- Consider generating simple preview PNGs alongside STL files for quick inspection.

3/ UX:
- Make the default command produce a valid STL in a predictable output folder.
- Add validation for invalid dimensions, self-intersections where detectable, and missing dependencies.
- Provide example commands for the house and torus workflows.

4/ Testing:
- Add smoke tests that generate each model into a temp directory and verify non-empty STL output.
- Add bounds/mesh sanity checks where the geometry library supports them.
- Add tests for shared primitives once duplication is extracted.

5/ Everything else:
- Add a README explaining what each folder generates and which dependencies are required.
- Add `.gitignore` rules for generated meshes if they are not intended source artifacts.
- Add an AGENTS.md if the repo will continue receiving automation.

6/ My suggetions:
1. Add a README with install, run, and output examples.
2. Extract shared geometry primitives from duplicated house scripts.
3. Add a simple CLI for model selection and dimensions.
4. Add STL generation smoke tests.
5. Separate generated artifacts from source code.
