"""Paso 1: separa cada página en viñetas, en orden de lectura de manga (derecha a izquierda)."""
import cv2
import numpy as np
from pathlib import Path

import config


def _reading_order(rects):
    rects = sorted(rects, key=lambda r: r[1])
    rows = []
    for r in rects:
        x, y, w, h = r
        if rows and y < rows[-1]["bottom"] - 0.3 * h:
            rows[-1]["items"].append(r)
            rows[-1]["bottom"] = max(rows[-1]["bottom"], y + h)
        else:
            rows.append({"items": [r], "bottom": y + h})
    ordered = []
    for row in rows:
        ordered += sorted(row["items"], key=lambda r: -r[0])  # derecha -> izquierda
    return ordered


def detect_panels(img):
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bw = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY_INV)  # contenido = blanco
    bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, np.ones((25, 25), np.uint8))
    contours, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    for c in contours:
        x, y, rw, rh = cv2.boundingRect(c)
        if rw * rh > 0.04 * w * h and rw > 0.15 * w and rh > 0.08 * h:
            rects.append((x, y, rw, rh))
    if len(rects) < 2:           # no se detectó nada fiable: usar la página entera
        return [(0, 0, w, h)]
    return _reading_order(rects)


def extract_all(pages):
    out = []
    for pi, page in enumerate(pages):
        img = cv2.imread(str(page))
        if img is None:
            print(f"  (saltando {page.name}: no se pudo leer)")
            continue
        for qi, (x, y, w, h) in enumerate(detect_panels(img)):
            p = config.WORK_DIR / "panels" / f"p{pi:03d}_v{qi:02d}.png"
            cv2.imwrite(str(p), img[y:y + h, x:x + w])
            out.append(p)
    print(f"  {len(out)} viñetas detectadas")
    return out
