"""Paso 5: anima cada viñeta (zoom suave estilo motion comic), añade audio, subtítulos en español y une todo."""
import subprocess
from pathlib import Path

from PIL import Image, ImageFilter, ImageEnhance

import config

W, H, FPS = config.WIDTH, config.HEIGHT, config.FPS


def _canvas(src, out):
    """Pone la viñeta en un lienzo 16:9 con fondo borroso."""
    im = Image.open(src).convert("RGB")
    bg_scale = max(W / im.width, H / im.height)
    bg = im.resize((int(im.width * bg_scale), int(im.height * bg_scale)))
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H)).filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.45)
    fg_scale = min(W / im.width, H / im.height)
    fg = im.resize((int(im.width * fg_scale), int(im.height * fg_scale)))
    bg.paste(fg, ((W - fg.width) // 2, (H - fg.height) // 2))
    bg.save(out)


def _clip(canvas, audio, dur, out):
    frames = int(dur * FPS)
    vf = (f"scale={W*2}:{H*2},zoompan=z='min(zoom+0.0005,1.12)':x='iw/2-(iw/zoom/2)'"
          f":y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(canvas), "-i", str(audio),
                    "-vf", vf, "-af", "apad", "-t", f"{dur:.3f}",
                    "-c:v", "libx264", "-c:a", "aac", "-ar", "44100", str(out)], check=True)


def _ts(s):
    ms = int(round(s * 1000))
    h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); sec, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def render_episode(scenes, name):
    cdir = config.WORK_DIR / "clips"
    clips, srt, offset, n = [], [], 0.0, 1
    for i, sc in enumerate(scenes):
        print(f"  clip {i + 1}/{len(scenes)}")
        canvas = cdir / f"c{i:04d}.png"
        _canvas(sc["image"], canvas)
        clip = cdir / f"c{i:04d}.mp4"
        _clip(canvas, sc["audio"], sc["duration"], clip)
        clips.append(clip)
        for ln in sc["lines"]:
            srt.append(f"{n}\n{_ts(offset + ln['start'])} --> {_ts(offset + ln['end'] + 0.3)}\n{ln['es']}\n")
            n += 1
        offset += sc["duration"]

    lst = cdir / "list.txt"
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    joined = config.OUT_DIR / f"{name}_sin_subs.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
                    "-i", str(lst), "-c", "copy", str(joined)], check=True)

    srt_name = f"{name}.srt"
    (config.OUT_DIR / srt_name).write_text("\n".join(srt), encoding="utf-8")
    final = config.OUT_DIR / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", joined.name,
                    "-vf", f"subtitles={srt_name}:force_style='FontSize=22,Outline=2,MarginV=40'",
                    "-c:a", "copy", final.name], check=True, cwd=config.OUT_DIR)
    print(f"  duración total: {offset / 60:.1f} min (meta del episodio: {config.EPISODE_SECONDS / 60:.0f} min)")
    return final
