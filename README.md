# GTA 6 Clipper (Claude skill)

Turns long GTA 6 streams into ready-to-post vertical clips. You give Claude a stream link (or ask it to find today's biggest streams), and it finds the best moments, cuts them to 9:16 with the face cam on top and the gameplay underneath, adds a hook and word-by-word captions, and opens one page where you watch, copy and post.

Made by Ray Fu ([@raycfu](https://www.instagram.com/raycfu)). Full walkthrough on YouTube, and more free skills and guides in the Skool community: https://skool.com/raycfu

## What you need

- A Mac or Linux computer (on Windows, use WSL)
- [Claude Code](https://claude.com/claude-code), which comes with the Claude Pro plan ($20/month)
- About 3 GB of free space for the tools and speech models, plus room for the streams you clip

Everything else is free and installs itself the first time: yt-dlp, ffmpeg, Whisper (speech to text that runs on your own computer) and a caption font. Nothing gets installed system-wide; it all lives in `~/.gta6-clipper`.

## Install

```bash
git clone https://github.com/raycfu/clipper ~/.claude/skills/gta6-clipper
```

Or download the folder and drag it into `~/.claude/skills/`. Then open Claude Code and say:

> set up the GTA clipper

Setup takes about 5 minutes the first time and ends with `READY`.

## Use it

Say one of these to Claude:

- `clip this stream: <YouTube, Twitch or Kick link>`
- `find me today's biggest GTA 6 streams and clip them`
- `look at what's working` (after a week of posting, with your YouTube channel link)

Claude will show you a table of the moments it kept and the ones it cut, render the clips, and open the gallery page. Your clips are saved in `~/GTA6 Clipper/runs/<date>/clips/`.

## How it works

1. **Find**: searches YouTube for the most viewed GTA 6 streams (live streams are skipped until the recording is up).
2. **Listen**: downloads only the audio, then builds a hype curve from how loud the streamer gets, YouTube's "most replayed" graph and, on YouTube stream recordings, how fast chat is moving. It transcribes the 25 hottest spots with Whisper on your computer.
3. **Pick**: Claude scores every moment with three questions. Would a stranger stop scrolling in two seconds? Does it make sense with zero context? Does it pay off inside the clip? One no and it's cut.
4. **Cut**: downloads only the minutes it needs and builds a 1080x1920 clip: face cam on top, gameplay underneath, a hook for the first 3 seconds, word-by-word captions, and audio at Shorts loudness. Every clip gets checked for length, a black face cam and missing captions.
5. **Post**: one page with every clip, a title, caption and hashtags with copy buttons, and a link to the exact second in the original stream so you can credit it. Nothing is ever posted for you.

Every week, `look at what's working` reads the public views on your Shorts, matches them to the clips the skill made, and updates `~/GTA6 Clipper/preferences.md` so the picks lean toward what your audience watches.

## Before you post

- Watch every clip first.
- Add something of your own (your hook, your take, a reaction). Channels of raw reposted clips get turned down for monetization.
- Credit the streamer, follow the clipping campaign's rules, and don't post the same clip twice on one account.
- Only clip streams you're allowed to clip. You're responsible for what you post.

## Troubleshooting

- **"Sign in to confirm you're not a bot" from YouTube**: run `export GTA6_COOKIES_BROWSER=chrome` (or `safari` / `firefox`) and try again, or say "set up the GTA clipper" again to update the downloader.
- **"This stream is still live"**: wait until the stream ends and the recording is up.
- **No chat signal**: chat speed only works on YouTube recordings of live streams. Twitch and Kick use loudness only.
- **Slow transcribing**: ask Claude to use the `base` model or fewer candidates (`--top 15`).

## Files

```
SKILL.md              instructions Claude follows
scripts/setup.sh      one-time install into ~/.gta6-clipper
scripts/find_streams.py   find the biggest GTA 6 streams
scripts/analyze.py    audio, hype curve, transcripts of the hot spots
scripts/cut.py        download only the needed minutes, render vertical clips
scripts/gallery.py    the page you post from
scripts/learn.py      weekly "look at what's working" report
scripts/common.py     shared helpers
```
