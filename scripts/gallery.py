"""Build one page with every finished clip, its caption and hashtags, and copy buttons.

Usage: python gallery.py --run "~/GTA6 Clipper/runs/<run>" [--no-open]
"""
import argparse
import html
import os
import subprocess
import sys

from common import hms, load


def esc(s):
    return html.escape(str(s or ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--no-open", action="store_true")
    a = ap.parse_args()
    run_dir = os.path.expanduser(a.run)
    clips = load(os.path.join(run_dir, "clips.json"), {}).get("clips", [])
    clips.sort(key=lambda c: -float(c.get("score") or 0))

    cards = []
    for c in clips:
        tags = " ".join(c.get("hashtags") or [])
        post = (c.get("caption") or "").strip() + ("\n\n" + tags if tags else "")
        src = c.get("url", "")
        if "youtube.com" in src or "youtu.be" in src:
            src += ("&" if "?" in src else "?") + f"t={int(c.get('start_s', 0))}s"
        ok = c.get("qc") == "ok"
        cards.append(f"""
<div class="card">
  <video src="{esc(c['file'])}" controls preload="metadata" playsinline></video>
  <div class="body">
    <div class="row"><span class="score">{esc(c.get('score'))}/10</span><span class="type">{esc(c.get('moment_type'))}</span>
      <span class="qc {'ok' if ok else 'warn'}">{'checks passed' if ok else esc(c.get('qc'))}</span></div>
    <h3>{esc(c.get('title'))}</h3>
    <p class="hook">Hook: {esc(c.get('hook'))}</p>
    <p class="why">{esc(c.get('why'))}</p>
    <textarea readonly>{esc(post)}</textarea>
    <div class="row">
      <button data-t="{esc(c.get('title'))}" onclick="cp(this, this.dataset.t)">Copy title</button>
      <button onclick="cp(this, this.closest('.body').querySelector('textarea').value)">Copy caption + hashtags</button>
      <a href="{esc(c['file'])}" download>Download</a>
    </div>
    <p class="src">From <a href="{esc(src)}" target="_blank">{esc(c.get('streamer'))} at {hms(c.get('start_s', 0))}</a>. Credit the streamer and add your own take before posting.</p>
  </div>
</div>""")

    page = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GTA 6 Clips</title><style>
:root{{--bg:#0e0e12;--card:#18181f;--fg:#f2f2f5;--mut:#9a9aa8;--acc:#ffd60a}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 -apple-system,Segoe UI,Roboto,sans-serif;padding:24px 16px}}
h1{{margin:0 0 4px}} .sub{{color:var(--mut);margin:0 0 24px}}
.grid{{display:grid;gap:20px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
.card{{background:var(--card);border-radius:16px;overflow:hidden}}
video{{width:100%;aspect-ratio:9/16;background:#000;display:block}}
.body{{padding:14px}} h3{{margin:8px 0 4px;font-size:17px}}
.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}
.score{{background:var(--acc);color:#111;font-weight:800;border-radius:8px;padding:2px 8px}}
.type{{color:var(--mut)}} .qc{{font-size:12px;border-radius:8px;padding:2px 8px}}
.qc.ok{{background:#1f3b2a;color:#7ee2a0}} .qc.warn{{background:#43301a;color:#ffc46b}}
.hook{{margin:2px 0;font-weight:700}} .why{{color:var(--mut);margin:4px 0 8px}}
textarea{{width:100%;box-sizing:border-box;height:92px;background:#101016;color:var(--fg);border:1px solid #2a2a35;border-radius:10px;padding:8px;font:inherit}}
button,a{{background:#2a2a35;color:var(--fg);border:0;border-radius:10px;padding:8px 12px;font:inherit;cursor:pointer;text-decoration:none}}
.src{{color:var(--mut);font-size:13px}} .src a{{background:none;padding:0;color:var(--acc)}}
</style></head><body>
<h1>GTA 6 Clips</h1><p class="sub">{len(clips)} clips, best first. Watch each one, cut anything that starts slow, then copy and post.</p>
<div class="grid">{''.join(cards)}</div>
<script>function cp(b,t){{navigator.clipboard.writeText(t).then(()=>{{const o=b.textContent;b.textContent='Copied';setTimeout(()=>b.textContent=o,1200)}})}}</script>
</body></html>"""
    out = os.path.join(run_dir, "index.html")
    with open(out, "w") as fh:
        fh.write(page)
    print(f"Gallery: {out}")
    if not a.no_open:
        opener = "open" if sys.platform == "darwin" else ("start" if os.name == "nt" else "xdg-open")
        subprocess.run([opener, out], shell=(os.name == "nt"), check=False)


if __name__ == "__main__":
    main()
