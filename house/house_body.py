#!/usr/bin/env python3
"""
Generate an ASCII STL for the house body.
- Watertight hollow body
- 2 mm wall thickness
- 2 mm floor thickness
- 2 mm ceiling thickness
- Front door opening
- Windows on back/left/right walls
"""

import math
from pathlib import Path

OUT_DIR = Path(__file__).parent

# House body dimensions (mm)
BODY_W = 160.0
BODY_D = 120.0
BODY_H = 120.0

WALL_THICKNESS = 2.0
CEILING_THICKNESS = 2.0
DOOR_W = 40.0
DOOR_H = 70.0
WINDOW_W = 30.0
WINDOW_H = 30.0
WINDOW_SILL_Z = 45.0


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


def unique_sorted(values):
    return sorted(set(values))


def write_body(path: Path):
    x0, x1 = 0.0, BODY_W
    y0, y1 = 0.0, BODY_D
    z0, z1 = 0.0, BODY_H

    xi0 = x0 + WALL_THICKNESS
    xi1 = x1 - WALL_THICKNESS
    yi0 = y0 + WALL_THICKNESS
    yi1 = y1 - WALL_THICKNESS
    zi0 = z0 + WALL_THICKNESS
    zi1 = z1 - CEILING_THICKNESS

    door_x0 = (BODY_W - DOOR_W) / 2.0
    door_x1 = door_x0 + DOOR_W
    door_z0 = z0
    door_z1 = door_z0 + DOOR_H

    back_win_x0 = (BODY_W - WINDOW_W) / 2.0
    back_win_x1 = back_win_x0 + WINDOW_W
    win_z0 = WINDOW_SILL_Z
    win_z1 = win_z0 + WINDOW_H

    side_win_y0 = (BODY_D - WINDOW_W) / 2.0
    side_win_y1 = side_win_y0 + WINDOW_W

    xs = unique_sorted([x0, xi0, door_x0, door_x1, back_win_x0, back_win_x1, xi1, x1])
    ys = unique_sorted([y0, yi0, side_win_y0, side_win_y1, yi1, y1])
    zs = unique_sorted([z0, zi0, win_z0, door_z1, win_z1, zi1, z1])

    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1

    def in_opening(xc, yc, zc):
        in_door = door_x0 < xc < door_x1 and y0 < yc < yi0 and door_z0 < zc < door_z1
        in_back_window = back_win_x0 < xc < back_win_x1 and yi1 < yc < y1 and win_z0 < zc < win_z1
        in_left_window = x0 < xc < xi0 and side_win_y0 < yc < side_win_y1 and win_z0 < zc < win_z1
        in_right_window = xi1 < xc < x1 and side_win_y0 < yc < side_win_y1 and win_z0 < zc < win_z1
        return in_door or in_back_window or in_left_window or in_right_window

    solid = [[[False for _ in range(nz)] for _ in range(ny)] for _ in range(nx)]
    for i in range(nx):
        xc = 0.5 * (xs[i] + xs[i + 1])
        for j in range(ny):
            yc = 0.5 * (ys[j] + ys[j + 1])
            for k in range(nz):
                zc = 0.5 * (zs[k] + zs[k + 1])

                in_outer = x0 < xc < x1 and y0 < yc < y1 and z0 < zc < z1
                in_inner = xi0 < xc < xi1 and yi0 < yc < yi1 and zi0 < zc < zi1
                filled = in_outer and not in_inner and not in_opening(xc, yc, zc)
                solid[i][j][k] = filled

    def is_solid(i, j, k):
        if i < 0 or i >= nx or j < 0 or j >= ny or k < 0 or k >= nz:
            return False
        return solid[i][j][k]

    with path.open("w", encoding="ascii") as f:
        f.write("solid house_body\n")

        for i in range(nx):
            for j in range(ny):
                for k in range(nz):
                    if not solid[i][j][k]:
                        continue

                    xa, xb = xs[i], xs[i + 1]
                    ya, yb = ys[j], ys[j + 1]
                    za, zb = zs[k], zs[k + 1]

                    # -X face
                    if not is_solid(i - 1, j, k):
                        add_quad(f, (xa, ya, za), (xa, yb, za), (xa, yb, zb), (xa, ya, zb))
                    # +X face
                    if not is_solid(i + 1, j, k):
                        add_quad(f, (xb, ya, za), (xb, ya, zb), (xb, yb, zb), (xb, yb, za))
                    # -Y face
                    if not is_solid(i, j - 1, k):
                        add_quad(f, (xa, ya, za), (xa, ya, zb), (xb, ya, zb), (xb, ya, za))
                    # +Y face
                    if not is_solid(i, j + 1, k):
                        add_quad(f, (xa, yb, za), (xb, yb, za), (xb, yb, zb), (xa, yb, zb))
                    # -Z face
                    if not is_solid(i, j, k - 1):
                        add_quad(f, (xa, ya, za), (xb, ya, za), (xb, yb, za), (xa, yb, za))
                    # +Z face
                    if not is_solid(i, j, k + 1):
                        add_quad(f, (xa, ya, zb), (xa, yb, zb), (xb, yb, zb), (xb, ya, zb))

        f.write("endsolid house_body\n")


def main():
    out = OUT_DIR / "house_body.stl"
    write_body(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
