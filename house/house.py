#!/usr/bin/env python3
"""
Generate house geometry as STL and colored 3MF files.
- house_body: hollow main body + annex + cylindrical tower with openings
- house_roof: two-slope roofs + conical tower roof (60% pitch), open underside
- house_merged: merged body+roof, scaled to fit 180x180x180 mm

Before each write, existing outputs are renamed to:
<name>.<YYYYMMDD-HHMMSS>.prev.<ext>
"""

import math
import subprocess
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

OUT_DIR = Path(__file__).parent
REPO_ROOT = OUT_DIR.parent

# Main body dimensions (mm) from: 7m x 4m x 5m
BODY_W = 7000.0
BODY_D = 4000.0
BODY_H = 5000.0

# Annex dimensions (mm) from: 6m x 3.5m x 4.5m
ANNEX_W = 6000.0
ANNEX_D = 3500.0
ANNEX_H = 4500.0
ANNEX_X0 = BODY_W
ANNEX_Y0 = 250.0
ANNEX_Z0 = 0.0

# Third body: cylindrical tower at left of main
# Diameter 3m -> radius 1.5m; height 6m
TOWER_RADIUS = 1500.0
TOWER_H = 6000.0
# Slight overlap into main body so the connection reads as intentional.
TOWER_CX = -TOWER_RADIUS + 850.0
TOWER_CY = BODY_D / 2.0

# Body parameters
EXTERIOR_WALL_THICKNESS = 200.0  # 20 cm
INTERIOR_WALL_THICKNESS = 100.0  # 10 cm
CEILING_THICKNESS = 200.0
DOOR_W = 1000.0
DOOR_H = 2100.0
WINDOW_W = 1200.0
WINDOW_H = 1200.0
WINDOW_SILL_Z = 1000.0
TOWER_WINDOW_H = 1100.0
TOWER_WINDOW_Z0 = 1700.0
TOWER_WINDOW_ANG_HALF_DEG = 6.0
TOWER_WINDOW_CENTERS_DEG = (110.0, 180.0, 250.0, 320.0)
TOWER_GRID_STEP = 25.0
TOWER_CONNECTOR_X0 = -250.0
TOWER_CONNECTOR_X1 = 0.0
TOWER_CONNECTOR_Y0 = TOWER_CY - 700.0
TOWER_CONNECTOR_Y1 = TOWER_CY + 700.0
TOWER_CONNECTOR_Z1 = BODY_H
PLINTH_PROJ = 120.0
PLINTH_H = 240.0
TOWER_BAND_PROJ = 120.0
TOWER_BAND_Z0 = TOWER_H - 650.0
TOWER_BAND_H = 180.0

# Roof parameters
ROOF_OVERHANG = 150.0
ROOF_SLOPE_PCT = 60.0
ANNEX_ROOF_SLOPE_PCT = 48.0
ROOF_THICKNESS = 120.0
CHIMNEY_W = 500.0
CHIMNEY_D = 500.0
CHIMNEY_H = 900.0
CHIMNEY_CAP_OVERHANG = 80.0
CHIMNEY_CAP_THICKNESS = 100.0
SKYLIGHT_W = 850.0
SKYLIGHT_D = 520.0
SKYLIGHT_H = 80.0
SKYLIGHT_INSET = 90.0

BODY_COLOR = "#FFFFFFFF"
ROOF_COLOR = "#C62828FF"
FLOOR_COLOR = "#111111FF"
FLOOR_OVERLAY_THICKNESS = 30.0


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def normalize(v):
    length = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def write_facet(f, p1, p2, p3):
    n = normalize(cross(sub(p2, p1), sub(p3, p1)))
    f.write(f"  facet normal {n[0]:.6e} {n[1]:.6e} {n[2]:.6e}\n")
    f.write("    outer loop\n")
    f.write(f"      vertex {p1[0]:.6e} {p1[1]:.6e} {p1[2]:.6e}\n")
    f.write(f"      vertex {p2[0]:.6e} {p2[1]:.6e} {p2[2]:.6e}\n")
    f.write(f"      vertex {p3[0]:.6e} {p3[1]:.6e} {p3[2]:.6e}\n")
    f.write("    endloop\n")
    f.write("  endfacet\n")


def add_quad(f, p1, p2, p3, p4):
    write_facet(f, p1, p2, p3)
    write_facet(f, p1, p3, p4)


def add_triangle(f, p1, p2, p3):
    write_facet(f, p1, p2, p3)


def append_triangle(tris, p1, p2, p3):
    tris.append((p1, p2, p3))


def append_quad(tris, p1, p2, p3, p4):
    append_triangle(tris, p1, p2, p3)
    append_triangle(tris, p1, p3, p4)


def append_box(tris, x0, x1, y0, y1, z0, z1):
    append_quad(tris, (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0))
    append_quad(tris, (x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1))
    append_quad(tris, (x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0))
    append_quad(tris, (x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1))
    append_quad(tris, (x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1))
    append_quad(tris, (x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0))


def append_cylinder(tris, cx, cy, radius, z0, z1, seg=96):
    bottom = []
    top = []
    for i in range(seg):
        a = 2.0 * math.pi * i / seg
        x = cx + radius * math.cos(a)
        y = cy + radius * math.sin(a)
        bottom.append((x, y, z0))
        top.append((x, y, z1))

    for i in range(seg):
        j = (i + 1) % seg
        append_quad(tris, bottom[i], bottom[j], top[j], top[i])

    center_bottom = (cx, cy, z0)
    center_top = (cx, cy, z1)
    for i in range(seg):
        j = (i + 1) % seg
        append_triangle(tris, center_bottom, bottom[j], bottom[i])
        append_triangle(tris, center_top, top[i], top[j])


def unique_sorted(values):
    return sorted(set(values))


def backup_existing(path: Path):
    if not path.exists():
        return None
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = path.with_name(f"{path.stem}.{ts}.prev{path.suffix}")
    path.rename(backup)
    return backup


def cleanup_old_backups(base_dir: Path):
    archive_dir = base_dir / "archive"
    for pattern in ("*.prev.stl", "*.old.stl", "*.prev.3mf", "*.old.3mf"):
        for p in base_dir.glob(pattern):
            if p.is_file():
                p.unlink()
        if archive_dir.exists():
            for p in archive_dir.glob(pattern):
                if p.is_file():
                    p.unlink()
    # Also clean the house/archive folder when running from /house.
    if base_dir.name == "house":
        archive_dir = base_dir / "archive"
        if archive_dir.exists():
            for pattern in ("*.prev.stl", "*.old.stl", "*.prev.3mf", "*.old.3mf"):
                for p in archive_dir.glob(pattern):
                    if p.is_file():
                        p.unlink()


def read_ascii_stl_triangles(path: Path):
    triangles = []
    verts = []
    with path.open("r", encoding="ascii") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 4 and parts[0] == "vertex":
                verts.append((float(parts[1]), float(parts[2]), float(parts[3])))
                if len(verts) == 3:
                    triangles.append((verts[0], verts[1], verts[2]))
                    verts = []
    return triangles


def write_ascii_stl_triangles(path: Path, name: str, triangles):
    with path.open("w", encoding="ascii") as f:
        f.write(f"solid {name}\n")
        for p1, p2, p3 in triangles:
            write_facet(f, p1, p2, p3)
        f.write(f"endsolid {name}\n")


def bounds_of_triangles(triangles):
    xs, ys, zs = [], [], []
    for p1, p2, p3 in triangles:
        for x, y, z in (p1, p2, p3):
            xs.append(x)
            ys.append(y)
            zs.append(z)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def translate_triangles(triangles, dx, dy, dz):
    out = []
    for p1, p2, p3 in triangles:
        out.append(
            (
                (p1[0] + dx, p1[1] + dy, p1[2] + dz),
                (p2[0] + dx, p2[1] + dy, p2[2] + dz),
                (p3[0] + dx, p3[1] + dy, p3[2] + dz),
            )
        )
    return out


def scale_and_rebase_to_fit(triangles, max_size=180.0):
    mins, maxs = bounds_of_triangles(triangles)
    dx = maxs[0] - mins[0]
    dy = maxs[1] - mins[1]
    dz = maxs[2] - mins[2]
    longest = max(dx, dy, dz)
    scale = 1.0 if longest == 0 else max_size / longest

    out = []
    for p1, p2, p3 in triangles:
        out.append(
            (
                ((p1[0] - mins[0]) * scale, (p1[1] - mins[1]) * scale, (p1[2] - mins[2]) * scale),
                ((p2[0] - mins[0]) * scale, (p2[1] - mins[1]) * scale, (p2[2] - mins[2]) * scale),
                ((p3[0] - mins[0]) * scale, (p3[1] - mins[1]) * scale, (p3[2] - mins[2]) * scale),
            )
        )
    new_mins, new_maxs = bounds_of_triangles(out)
    return out, scale, new_mins, new_maxs


def scale_and_rebase_parts(parts, max_size=180.0):
    all_triangles = []
    for _, triangles in parts:
        all_triangles.extend(triangles)
    mins, maxs = bounds_of_triangles(all_triangles)
    dx = maxs[0] - mins[0]
    dy = maxs[1] - mins[1]
    dz = maxs[2] - mins[2]
    longest = max(dx, dy, dz)
    scale = 1.0 if longest == 0 else max_size / longest

    scaled_parts = []
    for name, triangles in parts:
        scaled = []
        for p1, p2, p3 in triangles:
            scaled.append(
                (
                    ((p1[0] - mins[0]) * scale, (p1[1] - mins[1]) * scale, (p1[2] - mins[2]) * scale),
                    ((p2[0] - mins[0]) * scale, (p2[1] - mins[1]) * scale, (p2[2] - mins[2]) * scale),
                    ((p3[0] - mins[0]) * scale, (p3[1] - mins[1]) * scale, (p3[2] - mins[2]) * scale),
                )
            )
        scaled_parts.append((name, scaled))

    scaled_all = []
    for _, triangles in scaled_parts:
        scaled_all.extend(triangles)
    new_mins, new_maxs = bounds_of_triangles(scaled_all)
    return scaled_parts, scale, new_mins, new_maxs


def triangles_to_indexed_mesh(triangles):
    vertex_index = {}
    vertices = []
    indexed = []
    for p1, p2, p3 in triangles:
        tri = []
        for point in (p1, p2, p3):
            key = tuple(round(v, 6) for v in point)
            if key not in vertex_index:
                vertex_index[key] = len(vertices)
                vertices.append(key)
            tri.append(vertex_index[key])
        indexed.append(tuple(tri))
    return vertices, indexed


def write_3mf(path: Path, model_name: str, objects):
    resources = []
    build_items = []
    material_xml = []

    for color_index, obj in enumerate(objects):
        material_xml.append(
            f'<m:base name="{obj["name"]}" displaycolor="{obj["color"]}"/>'
        )

    for object_id, obj in enumerate(objects, start=1):
        vertices, triangles = triangles_to_indexed_mesh(obj["triangles"])
        verts_xml = "".join(
            f'<vertex x="{x:.6f}" y="{y:.6f}" z="{z:.6f}"/>' for x, y, z in vertices
        )
        tris_xml = "".join(
            f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in triangles
        )
        resources.append(
            (
                f'<object id="{object_id}" name="{obj["name"]}" type="model" pid="1" pindex="{object_id - 1}">'
                f"<mesh><vertices>{verts_xml}</vertices><triangles>{tris_xml}</triangles></mesh>"
                f"</object>"
            )
        )
        build_items.append(f'<item objectid="{object_id}"/>')

    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
        'xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">'
        "<metadata name=\"Title\">"
        f"{model_name}"
        "</metadata>"
        "<resources>"
        f'<m:basematerials id="1">{"".join(material_xml)}</m:basematerials>'
        f'{"".join(resources)}'
        "</resources>"
        f"<build>{''.join(build_items)}</build>"
        "</model>"
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>'
        "</Relationships>"
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
        "</Types>"
    )

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("3D/3dmodel.model", model_xml)


def body_rect(x0, y0, z0, w, d, h):
    return {
        "x0": x0,
        "x1": x0 + w,
        "y0": y0,
        "y1": y0 + d,
        "z0": z0,
        "z1": z0 + h,
    }


def body_triangles(include_ceilings=True):
    main = body_rect(0.0, 0.0, 0.0, BODY_W, BODY_D, BODY_H)
    annex = body_rect(ANNEX_X0, ANNEX_Y0, ANNEX_Z0, ANNEX_W, ANNEX_D, ANNEX_H)
    tower_connector = body_rect(
        TOWER_CONNECTOR_X0,
        TOWER_CONNECTOR_Y0,
        0.0,
        TOWER_CONNECTOR_X1 - TOWER_CONNECTOR_X0,
        TOWER_CONNECTOR_Y1 - TOWER_CONNECTOR_Y0,
        TOWER_CONNECTOR_Z1,
    )

    t = EXTERIOR_WALL_THICKNESS
    t_int = INTERIOR_WALL_THICKNESS

    # Main door on front wall
    main_door_x0 = (main["x0"] + main["x1"] - DOOR_W) / 2.0
    main_door_x1 = main_door_x0 + DOOR_W

    # Main windows: back + left only (right/adjoining wall window removed)
    main_back_wx0 = (main["x0"] + main["x1"] - WINDOW_W) / 2.0
    main_back_wx1 = main_back_wx0 + WINDOW_W
    main_side_wy0 = (main["y0"] + main["y1"] - WINDOW_W) / 2.0
    main_side_wy1 = main_side_wy0 + WINDOW_W

    # Annex windows on each exterior wall: front, back, right.
    annex_front_wx0 = (annex["x0"] + annex["x1"] - WINDOW_W) / 2.0
    annex_front_wx1 = annex_front_wx0 + WINDOW_W
    annex_back_wx0 = (annex["x0"] + annex["x1"] - WINDOW_W) / 2.0
    annex_back_wx1 = annex_back_wx0 + WINDOW_W
    annex_side_wy0 = (annex["y0"] + annex["y1"] - WINDOW_W) / 2.0
    annex_side_wy1 = annex_side_wy0 + WINDOW_W

    win_z0 = WINDOW_SILL_Z
    win_z1 = win_z0 + WINDOW_H

    # Interior communication openings between bodies.
    # Open the full shared wall area between main and annex, floor-to-ceiling (leave floor intact).
    shared_y0 = max(main["y0"], annex["y0"]) + EXTERIOR_WALL_THICKNESS
    shared_y1 = min(main["y1"], annex["y1"]) - EXTERIOR_WALL_THICKNESS
    shared_z0 = EXTERIOR_WALL_THICKNESS
    shared_z1 = min(main["z1"], annex["z1"]) - CEILING_THICKNESS

    # Open the shared wall between main and tower across the overlapping footprint.
    main_tower_open_x0 = -TOWER_RADIUS
    main_tower_open_x1 = min(BODY_W, TOWER_CX + TOWER_RADIUS + EXTERIOR_WALL_THICKNESS)
    main_tower_open_y0 = TOWER_CY - (TOWER_RADIUS + EXTERIOR_WALL_THICKNESS)
    main_tower_open_y1 = TOWER_CY + (TOWER_RADIUS + EXTERIOR_WALL_THICKNESS)
    # Keep a floor lip to avoid punching through the floor at the opening base.
    main_tower_open_z0 = EXTERIOR_WALL_THICKNESS
    main_tower_open_z1 = min(main["z1"], TOWER_H) - CEILING_THICKNESS

    # Grid lines for robust CSG-by-sampling.
    xs = [
        main["x0"], main["x0"] + t, main_door_x0, main_door_x1, main_back_wx0, main_back_wx1, main["x1"] - t, main["x1"],
        annex["x0"], annex["x0"] + t, annex_front_wx0, annex_front_wx1, annex_back_wx0, annex_back_wx1, annex["x1"] - t, annex["x1"],
        tower_connector["x0"], tower_connector["x1"],
    ]
    ys = [
        main["y0"], main["y0"] + t, main_side_wy0, main_side_wy1, main["y1"] - t, main["y1"],
        annex["y0"], annex["y0"] + t, annex_side_wy0, annex_side_wy1, annex["y1"] - t, annex["y1"],
        tower_connector["y0"], tower_connector["y1"],
    ]
    zs = [
        0.0,
        t,
        PLINTH_H,
        win_z0,
        DOOR_H,
        win_z1,
        TOWER_BAND_Z0,
        TOWER_BAND_Z0 + TOWER_BAND_H,
        TOWER_WINDOW_Z0,
        TOWER_WINDOW_Z0 + TOWER_WINDOW_H,
    ]
    if include_ceilings:
        zs.extend(
            [
                main["z1"] - CEILING_THICKNESS,
                main["z1"],
                annex["z1"] - CEILING_THICKNESS,
                annex["z1"],
                TOWER_H - CEILING_THICKNESS,
                TOWER_H,
            ]
        )
    else:
        zs.extend([main["z1"], annex["z1"], TOWER_H])
    # Local refinement around tower to keep the cylindrical profile readable.
    tower_x0 = TOWER_CX - TOWER_RADIUS
    tower_x1 = TOWER_CX + TOWER_RADIUS
    tower_y0 = TOWER_CY - TOWER_RADIUS
    tower_y1 = TOWER_CY + TOWER_RADIUS
    step = TOWER_GRID_STEP
    n_x = int(round((tower_x1 - tower_x0) / step))
    n_y = int(round((tower_y1 - tower_y0) / step))
    for n in range(n_x + 1):
        xs.append(tower_x0 + n * step)
    for n in range(n_y + 1):
        ys.append(tower_y0 + n * step)
    # Slight footprint expansion for plinths and tower belt.
    xs.extend(
        [
            main["x0"] - PLINTH_PROJ,
            main["x1"] + PLINTH_PROJ,
            annex["x0"] - PLINTH_PROJ,
            annex["x1"] + PLINTH_PROJ,
            TOWER_CX - TOWER_RADIUS - PLINTH_PROJ,
            TOWER_CX + TOWER_RADIUS + PLINTH_PROJ,
            TOWER_CX - TOWER_RADIUS - TOWER_BAND_PROJ,
            TOWER_CX + TOWER_RADIUS + TOWER_BAND_PROJ,
        ]
    )
    ys.extend(
        [
            main["y0"] - PLINTH_PROJ,
            main["y1"] + PLINTH_PROJ,
            annex["y0"] - PLINTH_PROJ,
            annex["y1"] + PLINTH_PROJ,
            TOWER_CY - TOWER_RADIUS - PLINTH_PROJ,
            TOWER_CY + TOWER_RADIUS + PLINTH_PROJ,
            TOWER_CY - TOWER_RADIUS - TOWER_BAND_PROJ,
            TOWER_CY + TOWER_RADIUS + TOWER_BAND_PROJ,
        ]
    )

    xs = unique_sorted(xs)
    ys = unique_sorted(ys)
    zs = unique_sorted(zs)

    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1

    def in_shell(rect, xc, yc, zc):
        ceiling_cut = CEILING_THICKNESS if include_ceilings else 0.0
        in_outer = rect["x0"] < xc < rect["x1"] and rect["y0"] < yc < rect["y1"] and rect["z0"] < zc < rect["z1"]
        in_inner = (
            rect["x0"] + t < xc < rect["x1"] - t
            and rect["y0"] + t < yc < rect["y1"] - t
            and rect["z0"] + t < zc < rect["z1"] - ceiling_cut
        )
        return in_outer and not in_inner

    def in_opening(xc, yc, zc):
        # Main body openings
        main_door = main_door_x0 < xc < main_door_x1 and main["y0"] < yc < main["y0"] + t and main["z0"] < zc < main["z0"] + DOOR_H
        main_back_win = main_back_wx0 < xc < main_back_wx1 and main["y1"] - t < yc < main["y1"] and win_z0 < zc < win_z1
        main_left_win = main["x0"] < xc < main["x0"] + t and main_side_wy0 < yc < main_side_wy1 and win_z0 < zc < win_z1

        # Annex openings (no left/adjoining wall window)
        annex_front_win = annex_front_wx0 < xc < annex_front_wx1 and annex["y0"] < yc < annex["y0"] + t and win_z0 < zc < win_z1
        annex_back_win = annex_back_wx0 < xc < annex_back_wx1 and annex["y1"] - t < yc < annex["y1"] and win_z0 < zc < win_z1
        annex_right_win = annex["x1"] - t < xc < annex["x1"] and annex_side_wy0 < yc < annex_side_wy1 and win_z0 < zc < win_z1

        # Tower windows: angular openings through cylindrical wall shell.
        dx = xc - TOWER_CX
        dy = yc - TOWER_CY
        r = math.sqrt(dx * dx + dy * dy)
        ang = math.degrees(math.atan2(dy, dx))
        if ang < 0:
            ang += 360.0
        tower_window_z = TOWER_WINDOW_Z0 < zc < TOWER_WINDOW_Z0 + TOWER_WINDOW_H
        tower_window_r = TOWER_RADIUS - t < r < TOWER_RADIUS
        tower_window_ang = False
        if tower_window_z and tower_window_r:
            for c in TOWER_WINDOW_CENTERS_DEG:
                d = abs(ang - c)
                d = min(d, 360.0 - d)
                if d < TOWER_WINDOW_ANG_HALF_DEG:
                    tower_window_ang = True
                    break

        # Interior openings so connected bodies communicate.
        open_main_annex = (
            main["x1"] - t < xc < annex["x0"] + t
            and shared_y0 < yc < shared_y1
            and shared_z0 < zc < shared_z1
        )
        # Cut the shared tower/main wall using the tower's own circular footprint
        # so we remove the remaining sliver without flattening the tower facade.
        tower_overlap_r = TOWER_RADIUS + EXTERIOR_WALL_THICKNESS
        in_tower_overlap = (
            (xc - TOWER_CX) * (xc - TOWER_CX) + (yc - TOWER_CY) * (yc - TOWER_CY)
            < tower_overlap_r * tower_overlap_r
        )
        open_main_tower = (
            main["x0"] - EXTERIOR_WALL_THICKNESS < xc < main_tower_open_x1
            and main["y0"] + EXTERIOR_WALL_THICKNESS < yc < main["y1"] - EXTERIOR_WALL_THICKNESS
            and in_tower_overlap
            and main_tower_open_z0 < zc < main_tower_open_z1
        )

        return (
            main_door
            or main_back_win
            or main_left_win
            or annex_front_win
            or annex_back_win
            or annex_right_win
            or tower_window_ang
            or open_main_annex
            or open_main_tower
        )

    def in_tower_shell(xc, yc, zc):
        dx = xc - TOWER_CX
        dy = yc - TOWER_CY
        r2 = dx * dx + dy * dy
        in_outer = r2 < TOWER_RADIUS * TOWER_RADIUS and 0.0 < zc < TOWER_H
        inner_r = TOWER_RADIUS - t
        ceiling_cut = CEILING_THICKNESS if include_ceilings else 0.0
        in_inner = r2 < inner_r * inner_r and t < zc < TOWER_H - ceiling_cut
        return in_outer and not in_inner

    def in_plinth_rect(rect, xc, yc, zc):
        return (
            rect["x0"] - PLINTH_PROJ < xc < rect["x1"] + PLINTH_PROJ
            and rect["y0"] - PLINTH_PROJ < yc < rect["y1"] + PLINTH_PROJ
            and 0.0 < zc < PLINTH_H
        )

    def in_tower_plinth(xc, yc, zc):
        dx = xc - TOWER_CX
        dy = yc - TOWER_CY
        r2 = dx * dx + dy * dy
        outer_r = TOWER_RADIUS + PLINTH_PROJ
        return r2 < outer_r * outer_r and 0.0 < zc < PLINTH_H

    def in_tower_belt(xc, yc, zc):
        dx = xc - TOWER_CX
        dy = yc - TOWER_CY
        r2 = dx * dx + dy * dy
        inner_r = TOWER_RADIUS
        outer_r = TOWER_RADIUS + TOWER_BAND_PROJ
        return inner_r * inner_r < r2 < outer_r * outer_r and TOWER_BAND_Z0 < zc < TOWER_BAND_Z0 + TOWER_BAND_H

    solid = [[[False for _ in range(nz)] for _ in range(ny)] for _ in range(nx)]
    for i in range(nx):
        xc = 0.5 * (xs[i] + xs[i + 1])
        for j in range(ny):
            yc = 0.5 * (ys[j] + ys[j + 1])
            for k in range(nz):
                zc = 0.5 * (zs[k] + zs[k + 1])
                filled = (
                    in_shell(main, xc, yc, zc)
                    or in_shell(annex, xc, yc, zc)
                    or in_shell(tower_connector, xc, yc, zc)
                    or in_tower_shell(xc, yc, zc)
                    or in_plinth_rect(main, xc, yc, zc)
                    or in_plinth_rect(annex, xc, yc, zc)
                    or in_tower_plinth(xc, yc, zc)
                    or in_tower_belt(xc, yc, zc)
                ) and not in_opening(xc, yc, zc)
                solid[i][j][k] = filled

    def is_solid(i, j, k):
        if i < 0 or i >= nx or j < 0 or j >= ny or k < 0 or k >= nz:
            return False
        return solid[i][j][k]

    tris = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if not solid[i][j][k]:
                    continue

                xa, xb = xs[i], xs[i + 1]
                ya, yb = ys[j], ys[j + 1]
                za, zb = zs[k], zs[k + 1]

                if not is_solid(i - 1, j, k):
                    append_quad(tris, (xa, ya, za), (xa, yb, za), (xa, yb, zb), (xa, ya, zb))
                if not is_solid(i + 1, j, k):
                    append_quad(tris, (xb, ya, za), (xb, ya, zb), (xb, yb, zb), (xb, yb, za))
                if not is_solid(i, j - 1, k):
                    append_quad(tris, (xa, ya, za), (xa, ya, zb), (xb, ya, zb), (xb, ya, za))
                if not is_solid(i, j + 1, k):
                    append_quad(tris, (xa, yb, za), (xb, yb, za), (xb, yb, zb), (xa, yb, zb))
                if not is_solid(i, j, k - 1):
                    append_quad(tris, (xa, ya, za), (xb, ya, za), (xb, yb, za), (xa, yb, za))
                if not is_solid(i, j, k + 1):
                    append_quad(tris, (xa, ya, zb), (xa, yb, zb), (xb, yb, zb), (xb, ya, zb))
    return tris


def write_body(path: Path):
    write_ascii_stl_triangles(path, "house_body", body_triangles(include_ceilings=True))


def append_roof_section(tris, x0, x1, y0, y1, z0, include_bottom_caps, add_chimney=False, slope_pct=ROOF_SLOPE_PCT, skylight_shift=0.38):
    slope = slope_pct / 100.0
    y_ridge = (y0 + y1) / 2.0
    run = y_ridge - y0
    z1 = z0 + slope * run

    o_fl = (x0, y0, z0)
    o_fr = (x1, y0, z0)
    o_rl = (x0, y1, z0)
    o_rr = (x1, y1, z0)
    o_tl = (x0, y_ridge, z1)
    o_tr = (x1, y_ridge, z1)

    def push_tri(p1, p2, p3):
        tris.append((p1, p2, p3))

    def push_quad(p1, p2, p3, p4):
        push_tri(p1, p2, p3)
        push_tri(p1, p3, p4)

    push_quad(o_fl, o_fr, o_tr, o_tl)
    push_quad(o_tl, o_tr, o_rr, o_rl)
    push_tri(o_fl, o_tl, o_rl)
    push_tri(o_fr, o_rr, o_tr)

    if include_bottom_caps:
        push_quad(o_fl, o_rl, o_rr, o_fr)

    if add_chimney:
        chim_cx = x0 + (x1 - x0) * 0.72
        chim_cy = y_ridge + (y1 - y_ridge) * 0.40
        # Slight embed into roof so it never appears to float.
        chim_z_base = z0 + slope * (y1 - chim_cy) - 1.5
        chim_x0 = chim_cx - CHIMNEY_W / 2.0
        chim_x1 = chim_cx + CHIMNEY_W / 2.0
        chim_y0 = chim_cy - CHIMNEY_D / 2.0
        chim_y1 = chim_cy + CHIMNEY_D / 2.0
        chim_z1 = chim_z_base + CHIMNEY_H

        push_quad((chim_x0, chim_y0, chim_z_base), (chim_x1, chim_y0, chim_z_base), (chim_x1, chim_y1, chim_z_base), (chim_x0, chim_y1, chim_z_base))
        push_quad((chim_x0, chim_y0, chim_z1), (chim_x0, chim_y1, chim_z1), (chim_x1, chim_y1, chim_z1), (chim_x1, chim_y0, chim_z1))
        push_quad((chim_x0, chim_y0, chim_z_base), (chim_x1, chim_y0, chim_z_base), (chim_x1, chim_y0, chim_z1), (chim_x0, chim_y0, chim_z1))
        push_quad((chim_x0, chim_y1, chim_z_base), (chim_x0, chim_y1, chim_z1), (chim_x1, chim_y1, chim_z1), (chim_x1, chim_y1, chim_z_base))
        push_quad((chim_x0, chim_y0, chim_z_base), (chim_x0, chim_y1, chim_z_base), (chim_x0, chim_y1, chim_z1), (chim_x0, chim_y0, chim_z1))
        push_quad((chim_x1, chim_y0, chim_z_base), (chim_x1, chim_y0, chim_z1), (chim_x1, chim_y1, chim_z1), (chim_x1, chim_y1, chim_z_base))

        cap_x0 = chim_x0 - CHIMNEY_CAP_OVERHANG
        cap_x1 = chim_x1 + CHIMNEY_CAP_OVERHANG
        cap_y0 = chim_y0 - CHIMNEY_CAP_OVERHANG
        cap_y1 = chim_y1 + CHIMNEY_CAP_OVERHANG
        cap_z0 = chim_z1
        cap_z1 = chim_z1 + CHIMNEY_CAP_THICKNESS
        push_quad((cap_x0, cap_y0, cap_z0), (cap_x1, cap_y0, cap_z0), (cap_x1, cap_y1, cap_z0), (cap_x0, cap_y1, cap_z0))
        push_quad((cap_x0, cap_y0, cap_z1), (cap_x0, cap_y1, cap_z1), (cap_x1, cap_y1, cap_z1), (cap_x1, cap_y0, cap_z1))
        push_quad((cap_x0, cap_y0, cap_z0), (cap_x1, cap_y0, cap_z0), (cap_x1, cap_y0, cap_z1), (cap_x0, cap_y0, cap_z1))
        push_quad((cap_x0, cap_y1, cap_z0), (cap_x0, cap_y1, cap_z1), (cap_x1, cap_y1, cap_z1), (cap_x1, cap_y1, cap_z0))
        push_quad((cap_x0, cap_y0, cap_z0), (cap_x0, cap_y1, cap_z0), (cap_x0, cap_y1, cap_z1), (cap_x0, cap_y0, cap_z1))
        push_quad((cap_x1, cap_y0, cap_z0), (cap_x1, cap_y0, cap_z1), (cap_x1, cap_y1, cap_z1), (cap_x1, cap_y1, cap_z0))

    # Low-profile attic skylight on front slope, slanted to match roof pitch.
    sky_cx = x0 + (x1 - x0) * skylight_shift
    sky_cy = y0 + (y_ridge - y0) * 0.52
    sky_x0 = sky_cx - SKYLIGHT_W / 2.0
    sky_x1 = sky_cx + SKYLIGHT_W / 2.0
    sky_y0 = sky_cy - SKYLIGHT_D / 2.0
    sky_y1 = sky_cy + SKYLIGHT_D / 2.0
    # Embed slightly so it blends into slope; top keeps same pitch as roof.
    z_at_y0 = z0 + slope * (sky_y0 - y0) - 0.8
    z_at_y1 = z0 + slope * (sky_y1 - y0) - 0.8

    b00 = (sky_x0, sky_y0, z_at_y0)
    b10 = (sky_x1, sky_y0, z_at_y0)
    b11 = (sky_x1, sky_y1, z_at_y1)
    b01 = (sky_x0, sky_y1, z_at_y1)

    top_x0 = sky_x0 + SKYLIGHT_INSET
    top_x1 = sky_x1 - SKYLIGHT_INSET
    top_y0 = sky_y0 + SKYLIGHT_INSET
    top_y1 = sky_y1 - SKYLIGHT_INSET
    z_top_y0 = z0 + slope * (top_y0 - y0) - 0.8 + SKYLIGHT_H
    z_top_y1 = z0 + slope * (top_y1 - y0) - 0.8 + SKYLIGHT_H
    t00 = (top_x0, top_y0, z_top_y0)
    t10 = (top_x1, top_y0, z_top_y0)
    t11 = (top_x1, top_y1, z_top_y1)
    t01 = (top_x0, top_y1, z_top_y1)

    # Tapered skylight reads more like an integrated roof lantern than a box.
    push_quad(b00, b10, b11, b01)
    push_quad(t00, t01, t11, t10)
    push_quad(b00, b10, t10, t00)
    push_quad(b01, t01, t11, b11)
    push_quad(b00, b01, t01, t00)
    push_quad(b10, t10, t11, b11)


def append_cone_roof(tris, cx, cy, base_z, radius, include_bottom_caps):
    slope = ROOF_SLOPE_PCT / 100.0
    z_apex = base_z + slope * radius
    apex = (cx, cy, z_apex)
    base_center = (cx, cy, base_z)
    seg = 72

    def ring_point(i):
        a = 2.0 * math.pi * i / seg
        return (cx + radius * math.cos(a), cy + radius * math.sin(a), base_z)

    for i in range(seg):
        p0 = ring_point(i)
        p1 = ring_point((i + 1) % seg)
        # Outer conical side.
        tris.append((p0, p1, apex))
        # Closed underside for merged output.
        if include_bottom_caps:
            tris.append((base_center, p1, p0))


def roof_triangles(include_bottom_caps: bool):
    tris = []

    # Main roof section
    append_roof_section(
        tris,
        x0=0.0 - ROOF_OVERHANG,
        x1=BODY_W + ROOF_OVERHANG,
        y0=0.0 - ROOF_OVERHANG,
        y1=BODY_D + ROOF_OVERHANG,
        z0=BODY_H,
        include_bottom_caps=include_bottom_caps,
        add_chimney=True,
        slope_pct=ROOF_SLOPE_PCT,
        skylight_shift=0.38,
    )

    # Annex roof section
    annex = body_rect(ANNEX_X0, ANNEX_Y0, ANNEX_Z0, ANNEX_W, ANNEX_D, ANNEX_H)
    append_roof_section(
        tris,
        x0=annex["x0"] - ROOF_OVERHANG,
        x1=annex["x1"] + ROOF_OVERHANG,
        y0=annex["y0"] - ROOF_OVERHANG,
        y1=annex["y1"] + ROOF_OVERHANG,
        z0=annex["z1"],
        include_bottom_caps=include_bottom_caps,
        add_chimney=False,
        slope_pct=ANNEX_ROOF_SLOPE_PCT,
        skylight_shift=0.42,
    )

    # Tower cone roof (60% pitch).
    append_cone_roof(
        tris,
        cx=TOWER_CX,
        cy=TOWER_CY,
        base_z=TOWER_H,
        radius=TOWER_RADIUS + ROOF_OVERHANG,
        include_bottom_caps=include_bottom_caps,
    )

    return tris


def write_roof(path: Path):
    tris = roof_triangles(include_bottom_caps=False)
    write_ascii_stl_triangles(path, "house_roof", tris)


def roof_triangles_closed_underside():
    return roof_triangles(include_bottom_caps=True)


def floor_overlay_triangles():
    tris = []
    z0 = EXTERIOR_WALL_THICKNESS
    z1 = z0 + FLOOR_OVERLAY_THICKNESS
    t = EXTERIOR_WALL_THICKNESS

    append_box(
        tris,
        0.0 + t,
        BODY_W - t,
        0.0 + t,
        BODY_D - t,
        z0,
        z1,
    )

    append_box(
        tris,
        ANNEX_X0 + t,
        ANNEX_X0 + ANNEX_W - t,
        ANNEX_Y0 + t,
        ANNEX_Y0 + ANNEX_D - t,
        z0,
        z1,
    )

    # Keep the tower floor just inside the inner wall and slightly clear of the main-body overlap.
    tower_floor_radius = TOWER_RADIUS - t - 20.0
    append_cylinder(tris, TOWER_CX, TOWER_CY, tower_floor_radius, z0, z1, seg=96)
    return tris


def main():
    body_path = OUT_DIR / "house_body.stl"
    roof_path = OUT_DIR / "house_roof.stl"
    merged_path = OUT_DIR / "house_merged.stl"
    body_3mf_path = OUT_DIR / "house_body.3mf"
    roof_3mf_path = OUT_DIR / "house_roof.3mf"
    merged_3mf_path = OUT_DIR / "house_merged.3mf"

    cleanup_old_backups(OUT_DIR)

    body_backup = backup_existing(body_path)
    roof_backup = backup_existing(roof_path)
    merged_backup = backup_existing(merged_path)
    body_3mf_backup = backup_existing(body_3mf_path)
    roof_3mf_backup = backup_existing(roof_3mf_path)
    merged_3mf_backup = backup_existing(merged_3mf_path)

    write_body(body_path)
    write_roof(roof_path)

    body_tris = read_ascii_stl_triangles(body_path)
    roof_tris_open = read_ascii_stl_triangles(roof_path)
    roof_tris_closed = roof_triangles_closed_underside()
    body_tris_open_top = body_triangles(include_ceilings=False)
    floor_tris = floor_overlay_triangles()

    write_3mf(
        body_3mf_path,
        "house_body",
        [
            {"name": "walls", "color": BODY_COLOR, "triangles": body_tris},
            {"name": "floors", "color": FLOOR_COLOR, "triangles": floor_tris},
        ],
    )
    write_3mf(
        roof_3mf_path,
        "house_roof",
        [{"name": "roof", "color": ROOF_COLOR, "triangles": roof_tris_open}],
    )

    scaled_parts, scale, mins, maxs = scale_and_rebase_parts(
        [("body", body_tris), ("roof", roof_tris_closed)],
        max_size=180.0,
    )
    scaled_body_tris = scaled_parts[0][1]
    scaled_roof_tris = scaled_parts[1][1]
    merged_tris = scaled_body_tris + scaled_roof_tris
    write_ascii_stl_triangles(merged_path, "house_merged", merged_tris)

    scaled_3mf_parts, _, _, _ = scale_and_rebase_parts(
        [("walls", body_tris_open_top), ("roof", roof_tris_closed), ("floors", floor_tris)],
        max_size=180.0,
    )
    scaled_wall_tris = scaled_3mf_parts[0][1]
    scaled_3mf_roof_tris = scaled_3mf_parts[1][1]
    scaled_floor_tris = scaled_3mf_parts[2][1]
    write_3mf(
        merged_3mf_path,
        "house_merged",
        [
            {"name": "walls", "color": BODY_COLOR, "triangles": scaled_wall_tris},
            {"name": "roof", "color": ROOF_COLOR, "triangles": scaled_3mf_roof_tris},
            {"name": "floors", "color": FLOOR_COLOR, "triangles": scaled_floor_tris},
        ],
    )

    if body_backup:
        print(f"Renamed {body_backup.name}")
    if roof_backup:
        print(f"Renamed {roof_backup.name}")
    if merged_backup:
        print(f"Renamed {merged_backup.name}")
    if body_3mf_backup:
        print(f"Renamed {body_3mf_backup.name}")
    if roof_3mf_backup:
        print(f"Renamed {roof_3mf_backup.name}")
    if merged_3mf_backup:
        print(f"Renamed {merged_3mf_backup.name}")
    print(f"Wrote {body_path}")
    print(f"Wrote {roof_path}")
    print(f"Wrote {merged_path}")
    print(f"Wrote {body_3mf_path}")
    print(f"Wrote {roof_3mf_path}")
    print(f"Wrote {merged_3mf_path}")
    print(
        "Merged scale={:.6f} size=({:.3f}, {:.3f}, {:.3f}) mm".format(
            scale,
            maxs[0] - mins[0],
            maxs[1] - mins[1],
            maxs[2] - mins[2],
        )
    )

    # Auto-update GitHub after each run.
    try:
        subprocess.run(["git", "add", "house", ".gitignore"], cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_ROOT, check=True, capture_output=True, text=True)
        if status.stdout.strip():
            msg = f"Update house outputs {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            subprocess.run(["git", "commit", "-m", msg], cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "push"], cwd=REPO_ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("GitHub updated.")
        else:
            print("No git changes to push.")
    except Exception as e:
        print(f"Git update failed: {e}")


if __name__ == "__main__":
    main()
