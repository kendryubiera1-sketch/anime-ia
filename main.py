import argparse
from pathlib import Path

import config
from pipeline import panels, script, colorize, voices, render


def main():
    ap = argparse.ArgumentParser(description="Manga -> episodio con voces en japonés y subtítulos en español")
    ap.add_argument("--title", default="", help="nombre de la obra (ayuda a la traducción)")
    ap.add_argument("--pages", default=str(config.INPUT_DIR), help="carpeta con las páginas")
    ap.add_argument("--name", default="episodio", help="nombre del archivo de salida")
    ap.add_argument("--redo-script", action="store_true", help="volver a leer/traducir las viñetas")
    args = ap.parse_args()

    config.ensure_dirs()
    pages = sorted(p for p in Path(args.pages).iterdir()
                   if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"})
    if not pages:
        raise SystemExit(f"No hay imágenes en {args.pages}")

    print("1/5 Detectando viñetas..."); files = panels.extract_all(pages)
    print("2/5 Leyendo texto y traduciendo...")
    scenes = script.build_scenes(files, args.title, config.WORK_DIR / f"{args.name}_script.json", args.redo_script)
    print("3/5 Coloreando...")
    for s in scenes:
        s["image"] = colorize.colorize_panel(s["image"])
    print("4/5 Voces en japonés..."); scenes = voices.add_audio(scenes)
    print("5/5 Montaje..."); out = render.render_episode(scenes, args.name)
    print(f"Listo: {out}")


if __name__ == "__main__":
    main()
