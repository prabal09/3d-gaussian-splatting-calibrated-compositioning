# 3D Gaussian Splatting - Calibrated Scene Compositing

Reconstruct a vehicle as a 3D Gaussian Splatting asset and composite it into a
calibrated real scene (the `c2` street snapshot) with correct metric scale,
perspective, occlusion, and a contact shadow - then drive it down the road.

Full design doc: see the project spec (`3DGS_Calibrated_Scene_Compositing.md`).

## Status
- [ ] **Phase 0** - calibration & ground-plane sanity (no GPU)
- [ ] Phase 1 - GS vehicle asset (CAD -> render -> gsplat) + Chamfer eval
- [ ] Phase 2 - static placement & composite
- [ ] Phase 3 - motion (drive.mp4)
- [ ] Phase 4 - realism (contact shadow, color match)

## Getting started (Phase 0)
```bash
python -m venv .venv && .venv\Scripts\activate   # Windows
pip install -r requirements.txt                  # Phase 0 deps only (no gsplat yet)

# 1) copy your c2 snapshot to data/c2_0_0_00_1.jpg
# 2) create calib/c2.json from calib/c2.example.json using your AvaCar calibration
# 3) run the sanity check
python calib/phase0_sanity.py
# -> open outputs/phase0/phase0_overlay.png
```
Phase 0 passes when the projected grid follows the road's perspective and the
reference cube sits flat on the asphalt at a plausible size.
