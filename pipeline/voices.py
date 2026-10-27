"""Paso 4: voces en japonés por línea de diálogo. Calcula la duración de cada escena."""
import wave
from pathlib import Path

import requests

import config

RATE, GAP = 24000, 0.3   # VOICEVOX genera wav mono de 24 kHz


def _silence(path, seconds):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b"\x00\x00" * int(RATE * seconds))


def _voicevox(text, speaker_id, out):
    base = config.VOICEVOX_URL
    q = requests.post(f"{base}/audio_query", params={"text": text, "speaker": speaker_id}, timeout=60)
    q.raise_for_status()
    s = requests.post(f"{base}/synthesis", params={"speaker": speaker_id}, json=q.json(), timeout=120)
    s.raise_for_status()
    Path(out).write_bytes(s.content)


def _synth(text, speaker, out):
    if config.TTS_BACKEND == "voicevox":
        sid = config.VOICE_IDS.get(speaker.lower(), config.VOICE_IDS["default"])
        _voicevox(text, sid, out)
    else:  # "silent": estima ~0.12 s por carácter
        _silence(out, max(0.8, len(text) * 0.12))


def _dur(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def _join(paths, out):
    with wave.open(str(paths[0]), "rb") as w0:
        params = w0.getparams()
    gap = b"\x00" * params.sampwidth * params.nchannels * int(params.framerate * GAP)
    with wave.open(str(out), "wb") as wo:
        wo.setparams(params)
        for i, p in enumerate(paths):
            with wave.open(str(p), "rb") as w:
                wo.writeframes(w.readframes(w.getnframes()))
            if i < len(paths) - 1:
                wo.writeframes(gap)


def add_audio(scenes):
    adir = config.WORK_DIR / "audio"
    for i, sc in enumerate(scenes):
        files, t = [], 0.0
        for j, ln in enumerate(sc["lines"]):
            f = adir / f"s{i:04d}_l{j:02d}.wav"
            _synth(ln["ja"], ln.get("speaker", "default"), f)
            d = _dur(f)
            ln["start"], ln["end"] = t, t + d
            t += d + GAP
            files.append(f)
        audio = adir / f"s{i:04d}.wav"
        if files:
            _join(files, audio)
            sc["duration"] = max(config.MIN_PANEL_SECONDS, _dur(audio) + 0.6)
        else:
            sc["duration"] = config.MIN_PANEL_SECONDS
            _silence(audio, sc["duration"])
        sc["audio"] = str(audio)
    return scenes
