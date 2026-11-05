"""Video-bench layout geometry, 4 Oct 2026.

Every number in the assembly guide that is not a vendor specification comes from here.
Sources of the fixed inputs:
  w   = 0.100 mm  Thorlabs S100LK, 100 +/- 4 um
  D   = 5.00 mm   Thorlabs P5000K1, 5.00 +/- 0.05 mm
  R   = 1.86      flight blur-to-slit ratio, 9.3 mrad x 5.0 mm / 25 um (Bench-Test-Plan section 4)
  FFD = 17.526 mm C-mount flange focal distance (C-mount standard)
  H   = 140 mm    beam height chosen for this layout (fits every post stack, see stacks())
  TRAVEL = 50 mm  DTS50 travel
  wedge gradient  NDL-25C-4: OD 0.04 to 4.0 over the coated length; ~0.045 OD/mm assumed (88 mm coating)
  pixel 5.5 um    assumption carried from the bench plan; measured in Step E
"""
import math, json

w, D, R, FFD, H, TRAVEL = 0.100, 5.00, 1.86, 17.526, 140.0, 50.0
PIX = 0.0055
OD_PER_MM = 0.045
GAP = 3.0            # pinhole housing front face to wedge coated face, mm
START_INSET = 3.0    # pinhole centre this far inside the coating at s = 0, mm

def L_of_d(d):
    """Pinhole-to-slit distance that gives source angle R*w/d."""
    return D * d / (R * w)

def table(dmin=17.0, dmax=25.0, step=0.5):
    rows, d = [], dmin
    while d <= dmax + 1e-9:
        L = L_of_d(d)
        rows.append((round(d, 1), round(L), round(L / 25.4, 2)))
        d += step
    return rows

# independent of d: strip motion on the detector per mm of stage travel
strip_mm_per_stage_mm = R * w / D                 # = d / L
rows_per_stage_mm = strip_mm_per_stage_mm / PIX
full_strip_mm = w + R * w                         # slit width + projected solar-disk blur
sweep_rows = TRAVEL * rows_per_stage_mm

def nominal(d=FFD):
    L = L_of_d(d)
    return dict(d=d, L=L, theta_mrad=R * w / d * 1e3,
                sweep_deg=math.degrees(math.atan(TRAVEL / 2 / L)) * 2,
                hole_halfwidth_at_100=TRAVEL / 2 * 100 / L)

def wedge_od(s):
    """OD under the pinhole centre at stage reading s (mm), measured from the coating start."""
    return 0.04 + OD_PER_MM * (s + START_INSET)

def stacks(cam_w=56.0):
    """Post-top heights each stack needs for a 140 mm beam."""
    return dict(camera_post_top=H - cam_w / 2, camera_post_top_if_52=H - 52 / 2,
                tube_top=H + 30.5 / 2, hood_top=H + 30.5 / 2)

if __name__ == "__main__":
    out = dict(
        L_table=table(),
        strip_mm_per_stage_mm=strip_mm_per_stage_mm,
        rows_per_stage_mm=rows_per_stage_mm,
        sweep_rows=sweep_rows,
        full_strip_um=full_strip_mm * 1e3,
        full_strip_rows=full_strip_mm / PIX,
        nominal_17p5=nominal(),
        nominal_22=nominal(22.0),
        od_s0=wedge_od(0), od_s50=wedge_od(50),
        tau_s0=wedge_od(0) * math.log(10), tau_s50=wedge_od(50) * math.log(10),
        s_at_tau4=(4 / math.log(10) - 0.04) / OD_PER_MM - START_INSET,
        stacks=stacks(),
        pitch_um_from_slope="p(um) = 1000 * (d/L) / slope(rows per mm) = %.1f / slope" % (strip_mm_per_stage_mm * 1000),
    )
    print(json.dumps(out, indent=1))
    json.dump(out, open(__file__.replace("geometry.py", "geometry.json"), "w"), indent=1)
