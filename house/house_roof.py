#!/usr/bin/env python3
"""
Generate an ASCII STL for the house roof.
- Simple two-slope roof (60% pitch)
- 2 mm shell with open underside
"""

import math
from pathlib import Path

OUT_DIR = Path(__file__).parent

BODY_W = 160.0
BODY_D = 120.0
BODY_H = 120.0
ROOF_OVERHANG = 5.0
ROOF_SLOPE_PCT = 60.0
ROOF_THICKNESS = 2.0


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


def write_roof(path: Path):
    x0 = -ROOF_OVERHANG
    x1 = BODY_W + ROOF_OVERHANG
    y0 = -ROOF_OVERHANG
    y1 = BODY_D + ROOF_OVERHANG
    z0 = BODY_H

    slope = ROOF_SLOPE_PCT / 100.0
    y_ridge = BODY_D / 2.0
    run = y_ridge - y0
    z1 = z0 + slope * run

    t = ROOF_THICKNESS
    slope_shift = t * math.sqrt(1.0 + slope * slope)

    xi0 = x0 + t
    xi1 = x1 - t
    zi0 = z0 + t
    y_front_inner = y0 + (t + slope_shift) / slope
    y_back_inner = y1 - (t + slope_shift) / slope
    z_ridge_inner = z1 - slope_shift

    # Outer roof vertices.
    o_fl = (x0, y0, z0)
    o_fr = (x1, y0, z0)
    o_rl = (x0, y1, z0)
    o_rr = (x1, y1, z0)
    o_tl = (x0, y_ridge, z1)
    o_tr = (x1, y_ridge, z1)

    # Inner roof vertices.
    i_fl = (xi0, y_front_inner, zi0)
    i_fr = (xi1, y_front_inner, zi0)
    i_rl = (xi0, y_back_inner, zi0)
    i_rr = (xi1, y_back_inner, zi0)
    i_tl = (xi0, y_ridge, z_ridge_inner)
    i_tr = (xi1, y_ridge, z_ridge_inner)

    with path.open("w", encoding="ascii") as f:
        f.write("solid house_roof\n")

        # Outer boundary (outward normals).
        add_quad(f, o_fl, o_fr, o_tr, o_tl)
        add_quad(f, o_tl, o_tr, o_rr, o_rl)
        add_triangle(f, o_fl, o_tl, o_rl)
        add_triangle(f, o_fr, o_rr, o_tr)

        # Inner boundary (reverse winding to bound cavity).
        add_quad(f, i_tl, i_tr, i_fr, i_fl)
        add_quad(f, i_rl, i_rr, i_tr, i_tl)
        add_triangle(f, i_rl, i_tl, i_fl)
        add_triangle(f, i_tr, i_rr, i_fr)

        f.write("endsolid house_roof\n")


def main():
    out = OUT_DIR / "house_roof.stl"
    write_roof(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
