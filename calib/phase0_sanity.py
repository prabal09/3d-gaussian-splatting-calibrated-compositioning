"""
Phase 0 - Calibration & ground-plane sanity check.

Projects a ground-plane grid and a reference cube (on z=0) through camera c2 and
overlays them on the c2 snapshot. If the grid follows the road's perspective and
the cube sits flat at plausible size, your calibration is good and you can proceed
to Phase 1. If not, fix calibration BEFORE building anything else.

No GPU / no gsplat needed. Run:  python calib/phase0_sanity.py
"""
import json
import os
import numpy as np
import cv2
import yaml


def load_cfg(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def load_calib(path):
    with open(path) as f:
        c = json.load(f)
    K = np.array(c["K"], dtype=np.float64)
    R = np.array(c["R"], dtype=np.float64)
    t = np.array(c["t"], dtype=np.float64).reshape(3)
    return K, R, t, c.get("image_size")


def project(X_world, K, R, t):
    """World points (N,3) -> image points (N,2) + validity mask (z_cam > 0).
    Assumes x_cam = R @ X_world + t (world->camera)."""
    X_world = np.asarray(X_world, dtype=np.float64).reshape(-1, 3)
    X_cam = (R @ X_world.T).T + t  # (N,3)
    z = X_cam[:, 2]
    valid = z > 1e-6
    uv = np.full((len(X_world), 2), np.nan)
    proj = (K @ X_cam[valid].T).T
    uv[valid] = proj[:, :2] / proj[:, 2:3]
    return uv, valid


def draw_grid(img, K, R, t, x_range, y_range, step):
    xs = np.arange(x_range[0], x_range[1] + 1e-9, step)
    ys = np.arange(y_range[0], y_range[1] + 1e-9, step)
    # lines parallel to the road (constant y)
    for y in ys:
        pts = np.array([[x, y, 0.0] for x in xs])
        uv, valid = project(pts, K, R, t)
        _polyline(img, uv, valid, (0, 200, 0))
    # lines across the road (constant x)
    for x in xs:
        pts = np.array([[x, y, 0.0] for y in ys])
        uv, valid = project(pts, K, R, t)
        _polyline(img, uv, valid, (0, 200, 0))


def draw_cube(img, K, R, t, size, center_xy):
    cx, cy = center_xy
    s = size
    # 8 corners, base on z=0
    corners = np.array([
        [cx,     cy,     0], [cx + s, cy,     0], [cx + s, cy + s, 0], [cx, cy + s, 0],
        [cx,     cy,     s], [cx + s, cy,     s], [cx + s, cy + s, s], [cx, cy + s, s],
    ], dtype=np.float64)
    uv, valid = project(corners, K, R, t)
    edges = [(0, 1), (1, 2), (2, 3), (3, 0),
             (4, 5), (5, 6), (6, 7), (7, 4),
             (0, 4), (1, 5), (2, 6), (3, 7)]
    for a, b in edges:
        if valid[a] and valid[b]:
            pa = tuple(np.round(uv[a]).astype(int))
            pb = tuple(np.round(uv[b]).astype(int))
            cv2.line(img, pa, pb, (0, 0, 255), 2, cv2.LINE_AA)


def _polyline(img, uv, valid, color):
    pts = uv[valid]
    for i in range(len(pts) - 1):
        pa = tuple(np.round(pts[i]).astype(int))
        pb = tuple(np.round(pts[i + 1]).astype(int))
        cv2.line(img, pa, pb, color, 1, cv2.LINE_AA)


def main():
    cfg = load_cfg()
    img = cv2.imread(cfg["scene_image"])
    if img is None:
        raise FileNotFoundError(f"Could not read scene image: {cfg['scene_image']}")
    K, R, t, _ = load_calib(cfg["calibration"])

    g = cfg["grid"]
    draw_grid(img, K, R, t, g["x_range"], g["y_range"], g["step"])
    c = cfg["cube"]
    draw_cube(img, K, R, t, c["size"], c["center_xy"])

    os.makedirs(cfg["output_dir"], exist_ok=True)
    out = os.path.join(cfg["output_dir"], "phase0_overlay.png")
    cv2.imwrite(out, img)
    print(f"Wrote {out} - open it and check: grid follows the road, cube sits flat & plausibly sized.")


if __name__ == "__main__":
    main()
