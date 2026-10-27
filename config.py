from pathlib import Path

ROOT = Path(__file__).parent
INPUT_DIR = ROOT / "input" / "pages"   # páginas del manga (png/jpg), en orden de nombre
WORK_DIR = ROOT / "work"
OUT_DIR = ROOT / "output"

# Vídeo
WIDTH, HEIGHT, FPS = 1920, 1080, 24
EPISODE_SECONDS = 24 * 60              # meta del episodio completo (24 min)
MIN_PANEL_SECONDS = 2.5                # duración mínima de cada viñeta

# LLM (lee el manga: texto japonés + traducción al español)
LLM_MODEL = "claude-sonnet-5-5"        # requiere la variable ANTHROPIC_API_KEY

# Voces en japonés: "silent" (prueba sin voz) o "voicevox" (motor local gratuito)
TTS_BACKEND = "silent"
VOICEVOX_URL = "http://127.0.0.1:50021"
VOICE_IDS = {"narrador": 2, "default": 3}  # ids de VOICEVOX; añade personajes aquí


def ensure_dirs():
    for d in (WORK_DIR, OUT_DIR, WORK_DIR / "panels", WORK_DIR / "audio", WORK_DIR / "clips"):
        d.mkdir(parents=True, exist_ok=True)
