#!/usr/bin/env python3
"""Kids cartoon video assembler: animated scenes + narration -> vertical MP4.

Usage: python3 render.py [--scale 720] [--only v01,v02]
Renders every video in specs_batch*.json whose scenes (>=1) and narration exist.
"""
import argparse, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FPS = 24
XF = 0.7          # crossfade seconds
LEAD = 0.4        # silence before narration
TAIL = 1.0        # silence after narration
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

PALETTE = ["#E84D8A", "#5A8DEE", "#F5A623", "#7D53DE", "#2FB47C", "#E8552F", "#199AB0"]

def ff():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def audio_duration(path):
    out = subprocess.run([ff(), "-i", path, "-f", "null", "-"], capture_output=True, text=True).stderr
    m = re.findall(r"time=(\d+):(\d+):([\d.]+)", out)
    if not m:
        raise RuntimeError(f"cannot probe {path}")
    h, mi, s = m[-1]
    return int(h) * 3600 + int(mi) * 60 + float(s)

def title_png(text, out, W=720, H=1280, color=PALETTE[0]):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = 62
    while True:
        f = ImageFont.truetype(FONT, size)
        words = text.split()
        lines, cur = [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if d.textlength(t, font=f) <= W - 200:
                cur = t
            else:
                lines.append(cur); cur = w
        lines.append(cur)
        if len(lines) <= 2 or size < 46:
            break
        size -= 5
    tw = max(d.textlength(l, font=f) for l in lines)
    lh = size + 16
    bw, bh = tw + 90, lh * len(lines) + 48
    x0, y0 = (W - bw) / 2, 140
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=48, fill=(255, 255, 255, 216))
    y = y0 + 24
    for l in lines:
        lw = d.textlength(l, font=f)
        d.text(((W - lw) / 2, y), l, font=f, fill=color, stroke_width=2, stroke_fill=(255, 255, 255))
        y += lh
    img.save(out)

ZOOMS = [
    ("min(1.0+{amt}*on/(D-1),{maxz})", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),          # zoom in
    ("{maxz}-{amt}*on/(D-1)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),                    # zoom out
    ("{maxz}", "(iw-iw/zoom)*on/(D-1)", "ih/2-(ih/zoom/2)"),                              # pan ->
    ("{maxz}", "(iw-iw/zoom)*(1-on/(D-1))", "ih/2-(ih/zoom/2)"),                          # pan <-
    ("{maxz}", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*(1-on/(D-1))"),                          # pan up
    ("{maxz}", "iw/2-(iw/zoom/2)", "(ih-ih/zoom)*on/(D-1)"),                              # pan down
]

def render(vid, title, scenes, audio, out, scale=720):
    W, H = scale, int(scale * 16 / 9)
    adur = audio_duration(audio)
    T = LEAD + adur + TAIL
    n = len(scenes)
    d = (T + (n - 1) * XF) / n
    frames = int(round(d * FPS)) + 4
    title_png(title, f"{ROOT}/frames/{vid}_title.png", W, H, PALETTE[int(vid[1:]) % len(PALETTE)])

    inputs, filt = [], []
    pre = f"scale={int(W*1.34)}:{int(H*1.34)}:force_original_aspect_ratio=increase,crop={int(W*1.34)}:{int(H*1.34)}"
    for i, s in enumerate(scenes):
        inputs += ["-i", s]
        z, x, y = ZOOMS[i % len(ZOOMS)]
        amt, maxz = 0.16, 1.16
        zx = z.format(amt=amt, maxz=maxz).replace("D", str(frames))
        xe = x.replace("D", str(frames))
        ye = y.replace("D", str(frames))
        filt.append(
            f"[{i}:v]{pre},zoompan=z='{zx}':x='{xe}':y='{ye}':d={frames}:s={W}x{H}:fps={FPS},"
            f"setsar=1,format=yuv420p[v{i}]"
        )
    if n == 1:
        filt.append("[v0]trim=duration=%.3f,setpts=PTS-STARTPTS[xv]" % T)
    else:
        prev = "v0"
        for i in range(1, n):
            off = i * d - XF
            lbl = f"x{i}" if i < n - 1 else "xv"
            filt.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={off:.3f}[{lbl}]")
            prev = lbl
    aid = n
    inputs += ["-i", audio]
    filt.append(
        f"[{aid}:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},apad,atrim=duration={T:.3f},"
        f"afade=t=out:st={T-0.9:.3f}:d=0.9,volume=1.0[aud]"
    )
    tid = n + 1
    inputs += ["-loop", "1", "-t", "3.6", "-i", f"{ROOT}/frames/{vid}_title.png"]
    filt.append(f"[{tid}:v]format=rgba,fade=t=in:st=0:d=0.4,fade=t=out:st=2.9:d=0.6[tit]")
    filt.append("[xv][tit]overlay=0:0:enable='lte(t,3.6)'[vout]")
    cmd = [ff(), "-y", *inputs, "-filter_complex", ";".join(filt),
           "-map", "[vout]", "-map", "[aud]",
           "-c:v", "libx264", "-preset", "fast", "-crf", "31", "-r", str(FPS),
           "-pix_fmt", "yuv420p", "-movflags", "+faststart",
           "-c:a", "aac", "-b:a", "96k", "-ac", "1", "-t", f"{T:.3f}", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:]); sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=int, default=720)
    ap.add_argument("--only", help="comma separated video ids")
    ap.add_argument("--outprefix", default="", help="extra dir/file prefix for outputs")
    args = ap.parse_args()
    specs = []
    for f in sorted(glob.glob(f"{ROOT}/specs_batch*.json")):
        specs += json.load(open(f))["videos"]
    for v in specs:
        vid = v["id"]
        if args.only and vid not in args.only.split(","):
            continue
        scenes = sorted(glob.glob(f"{ROOT}/images/{vid}_s*.jpg"))
        audio = f"{ROOT}/audio/{vid}.mp3"
        outdir = f"{ROOT}/videos/{args.outprefix}" if args.outprefix else f"{ROOT}/videos"
        os.makedirs(outdir, exist_ok=True)
        out = f"{outdir}/{vid}_{v['slug']}.mp4"
        if not os.path.exists(audio):
            print(f"{vid}: no narration yet, skipping"); continue
        if not scenes:
            print(f"{vid}: no scenes ready, skipping"); continue
        if os.path.exists(out):
            print(f"{vid}: already rendered"); continue
        print(f"{vid}: rendering {len(scenes)} scene(s) -> {out} ...", flush=True)
        render(vid, v["title"], scenes, audio, out, args.scale)
        print(f"{vid}: DONE ({os.path.getsize(out)/1e6:.1f} MB)", flush=True)

if __name__ == "__main__":
    main()
