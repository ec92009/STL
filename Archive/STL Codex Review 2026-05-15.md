# STL Codex Review 2026-05-15

1/ General architecture:
- The repo has two similar model folders, `house/` and `torus_stl/`, with duplicated files. Consolidate shared geometry primitives and make each model a small entry point.
- Add project metadata so dependencies, output paths, and supported commands are not implicit.

2/ UI:
- There is no UI, which is fine for a geometry-generation repo. The equivalent need is previewability: generated renders, thumbnails, or documented output screenshots.
- If scripts generate STL files, standardize output filenames and include a quick visual preview workflow.

3/ UX:
- The developer workflow is currently opaque. A new user needs to know which script to run, what it emits, and where outputs land.
- Add examples for generating the house and torus variants with expected parameters.

4/ Testing:
- No tests were found. Add tests that generated meshes are non-empty, manifold where expected, and within expected bounding boxes.
- Add a smoke test that runs each generator into a temporary output directory.

5/ Everything else:
- Add README and dependency documentation before expanding model complexity.
- Keep generated STL outputs out of source unless they are intentionally curated examples.

6/ My suggetions:
1. Add README with run commands, dependencies, and output examples.
2. Consolidate duplicated geometry code between `house/` and `torus_stl/`.
3. Add mesh smoke tests for non-empty output and bounding boxes.
4. Standardize output directories and generated file names.
5. Add preview images for curated example models.
