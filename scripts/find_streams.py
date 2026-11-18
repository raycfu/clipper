"""Find today's biggest GTA 6 streams on YouTube.

Usage:
  python find_streams.py                       # GTA 6 streams from this week, longest + most viewed
  python find_streams.py --query "GTA 6 xQc" --when today --max 5
"""
import argparse
import urllib.parse

import yt_dlp

from common import WORK, explain_download_error, hms, save, ydl_opts

# YouTube search filter codes: upload date
WHEN = {"hour": "EgIIAQ%3D%3D", "today": "EgIIAg%3D%3D", "week": "EgIIAw%3D%3D", "month": "EgIIBA%3D%3D"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="GTA 6 stream")
    ap.add_argument("--when", choices=list(WHEN), default="week")
    ap.add_argument("--min-minutes", type=int, default=45, help="skip anything shorter (we want full streams)")
    ap.add_argument("--max", type=int, default=8)
    ap.add_argument("--include-live", action="store_true", help="include streams that are live right now")
    a = ap.parse_args()

    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(a.query) + "&sp=" + WHEN[a.when]
    try:
        with yt_dlp.YoutubeDL(ydl_opts(extract_flat="in_playlist", playlistend=60)) as ydl:
            info = ydl.extract_info(url, download=False)
    except yt_dlp.utils.DownloadError as e:
        raise SystemExit(explain_download_error(e))

    rows, seen = [], set()
    for e in info.get("entries") or []:
        if not e or e.get("ie_key") not in (None, "Youtube") or e.get("id") in seen:
            continue
        seen.add(e.get("id"))
        live = e.get("live_status") == "is_live"
        dur = e.get("duration") or 0
        if live and not a.include_live:
            continue
        if not live and dur < a.min_minutes * 60:
            continue
        rows.append({
            "id": e.get("id"),
            "url": f"https://www.youtube.com/watch?v={e.get('id')}",
            "title": e.get("title"),
            "channel": e.get("channel") or e.get("uploader"),
            "duration": dur,
            "views": e.get("view_count") or 0,
            "live": live,
        })

    rows.sort(key=lambda r: r["views"], reverse=True)
    rows = rows[: a.max]
    save(WORK / "streams.json", rows)

    if not rows:
        print("No matching streams found. Try --when month or a different --query.")
        return
    print(f"Top {len(rows)} GTA 6 streams ({a.when}):")
    for i, r in enumerate(rows, 1):
        tag = "LIVE" if r["live"] else hms(r["duration"])
        print(f"{i}. [{tag}] {r['views']:,} views | {r['channel']} | {r['title']}\n   {r['url']}")
    print(f"\nSaved to {WORK / 'streams.json'}")


if __name__ == "__main__":
    main()
