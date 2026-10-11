import numpy as np
# 16 WS2812B on a helix: strip at r=8.5 (16mm post + PCB), LED face r=10, 144/m pitch, ~10mm strip width per turn
r_strip, r_led, pitch, rise_turn, N = 8.5, 10.0, 1000/144, 10.0, 16
dphi = pitch / r_strip
phi = np.arange(N) * dphi
z = phi / (2*np.pi) * rise_turn
L = np.stack([r_led*np.cos(phi), r_led*np.sin(phi), z], 1)
nL = np.stack([np.cos(phi), np.sin(phi), 0*phi], 1)
print(f"LEDs/turn {2*np.pi/dphi:.1f}, azimuth step {np.degrees(dphi):.0f} deg, height {z[-1]:.0f} mm")
for R in [12.5, 13, 14, 15, 16, 18, 20, 22]:
    a = np.linspace(0, 2*np.pi, 360, endpoint=False)
    zz = np.linspace(z[0]+rise_turn*0.5, z[-1]-rise_turn*0.5, 60)   # central band, skip ends
    A, Z = np.meshgrid(a, zz)
    P = np.stack([R*np.cos(A), R*np.sin(A), Z], -1)
    nP = np.stack([np.cos(A), np.sin(A), 0*A], -1)
    E = np.zeros(A.shape)
    for i in range(N):
        v = P - L[i]; d = np.linalg.norm(v, axis=-1); u = v / d[..., None]
        ce = np.clip((u*nL[i]).sum(-1), 0, None); ci = np.clip((u*nP).sum(-1), 0, None)
        E += ce*ci/d**2
    print(f"diffuser ID {2*R:4.0f} mm  gap {R-r_led:4.1f} mm  min/max {E.min()/E.max():.2f}  (std/mean {E.std()/E.mean():.2f})")
