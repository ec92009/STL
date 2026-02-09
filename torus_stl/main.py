#!/usr/bin/env python3
"""
Generate an ASCII STL for a torus.
Major diameter: 100mm
Minor (tube) diameter: 30mm
"""

import math
from pathlib import Path

# Dimensions in mm
MAJOR_DIAMETER = 100.0
MINOR_DIAMETER = 30.0

# Resolution
SEG_MAJOR = 180  # around the main ring
SEG_MINOR = 90   # around the tube

OUTPUT = Path(__file__).with_name("torus.stl")


def torus_point(R, r, u, v):
    # u: angle around main ring, v: angle around tube
    cu, su = math.cos(u), math.sin(u)
    cv, sv = math.cos(v), math.sin(v)
    x = (R + r * cv) * cu
    y = (R + r * cv) * su
    z = r * sv
    return (x, y, z)


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


def main():
    R = MAJOR_DIAMETER / 2.0
    r = MINOR_DIAMETER / 2.0

    du = 2.0 * math.pi / SEG_MAJOR
    dv = 2.0 * math.pi / SEG_MINOR

    with OUTPUT.open("w", encoding="ascii") as f:
        f.write("solid torus\n")
        for i in range(SEG_MAJOR):
            u0 = i * du
            u1 = (i + 1) * du
            for j in range(SEG_MINOR):
                v0 = j * dv
                v1 = (j + 1) * dv

                p00 = torus_point(R, r, u0, v0)
                p10 = torus_point(R, r, u1, v0)
                p11 = torus_point(R, r, u1, v1)
                p01 = torus_point(R, r, u0, v1)

                # Two triangles per quad
                write_facet(f, p00, p10, p11)
                write_facet(f, p00, p11, p01)
        f.write("endsolid torus\n")

    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
