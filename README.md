# Manga → episodio (prototipo)

Convierte páginas de manga en un vídeo tipo *motion comic* con voces en japonés
y subtítulos en español.

## Requisitos
- Python 3.10+ y `ffmpeg` instalado (con soporte de subtítulos/libass)
- `pip install -r requirements.txt`
- `export ANTHROPIC_API_KEY=tu_clave`

## Uso
1. Pon las páginas (png/jpg, en orden de nombre) en `input/pages/`
2. `python main.py --title "Nombre del manga" --name capitulo1`
3. El vídeo y el .srt quedan en `output/`

## Voces reales
Instala VOICEVOX (motor local gratuito), ábrelo y en `config.py` pon
`TTS_BACKEND = "voicevox"`. Asigna una voz distinta por personaje en `VOICE_IDS`.

## Qué falta para llegar a un anime de 24 min
- `pipeline/colorize.py`: conectar un modelo de colorización con referencias por personaje
- Animar con modelos de imagen→vídeo en vez del zoom (en `render._clip`)
- Detección de viñetas más robusta (viñetas sin bordes o solapadas caen a página completa)
- Música y efectos de sonido
- Revisar los derechos de autor antes de publicar
