"""Paso 2: un modelo con visión lee cada viñeta (texto japonés), identifica quién habla y traduce al español."""
import base64
import json
from pathlib import Path

from anthropic import Anthropic

import config

PROMPT = """Eres el adaptador de un manga a anime. Mira esta viñeta{title}.
Devuelve SOLO un JSON, sin texto extra ni ``` , con este formato:
{{"lines": [{{"speaker": "nombre del personaje o 'narrador'", "ja": "texto japonés exacto del globo o cuadro", "es": "traducción natural al español"}}]}}
Orden de lectura: de derecha a izquierda y de arriba abajo. Si no hay texto, devuelve {{"lines": []}}.
No incluyas onomatopeyas salvo que sean importantes para la escena."""


def _read_panel(client, path, title):
    data = base64.standard_b64encode(Path(path).read_bytes()).decode()
    msg = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": data}},
            {"type": "text", "text": PROMPT.format(title=f" de «{title}»" if title else "")},
        ]}],
    )
    text = msg.content[0].text.strip().strip("`").removeprefix("json").strip()
    try:
        return json.loads(text).get("lines", [])
    except json.JSONDecodeError:
        return []


def build_scenes(panel_files, title, cache_path, force=False):
    cache_path = Path(cache_path)
    if cache_path.exists() and not force:
        print("  usando guion en caché (usa --redo-script para rehacerlo)")
        return json.loads(cache_path.read_text(encoding="utf-8"))
    client = Anthropic()
    scenes = []
    for i, p in enumerate(panel_files, 1):
        print(f"  viñeta {i}/{len(panel_files)}")
        scenes.append({"image": str(p), "lines": _read_panel(client, p, title)})
    cache_path.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding="utf-8")
    return scenes
