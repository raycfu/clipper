---
name: gta6-clipper
description: Turns long GTA 6 streams (YouTube, Twitch or Kick) into ready-to-post vertical clips. It finds the biggest streams, downloads only the audio, builds a hype curve from loudness, YouTube's most-replayed graph and chat speed, transcribes the hot moments locally with Whisper, picks the best moments with a harsh filter, then cuts 9:16 clips with the face cam on top, gameplay underneath, a 3-second hook and word-by-word captions, plus a gallery page with captions and hashtags. Use it when the user says "set up the GTA clipper", "clip this stream", "find me today's biggest GTA 6 streams and clip them", "look at what's working", or asks to make Shorts/TikToks/Reels from a GTA (or any gaming) stream.
---

# GTA 6 Clipper

You turn a 4-hour stream into a handful of clips worth posting. The scripts do the heavy lifting on the user's computer for free; **your job is the judgment**: picking moments, writing hooks, reading the face cam position off a frame, and being honest about what's good.

Paths used below:
- `SKILL` = this skill's folder (the folder this file is in)
- `PY` = `~/.gta6-clipper/venv/bin/python`
- `WORK` = `~/GTA6 Clipper` (every stream, run and clip lives here)

Always run scripts as `cd "$SKILL/scripts" && "$PY" <script>.py ...`.

## 0. Setup ("set up the GTA clipper")

1. Run `bash "$SKILL/scripts/setup.sh"`. It installs uv, Python 3.12, yt-dlp, faster-whisper, ffmpeg and Pillow into `~/.gta6-clipper` only, plus the free Whisper models. First run takes a few minutes; later runs are instant.
2. It ends with `READY`. If it fails, show the user the last lines and fix the cause (usually no internet, or the user declined an install).
3. Create `WORK/preferences.md` if it doesn't exist, with the default rules from section 3 under a heading "My clip rules". This is the file the weekly review updates.
4. Tell the user it's ready and the two things they can say next: "clip this stream: <link>" or "find me today's biggest GTA 6 streams and clip them".

If `PY` doesn't exist when the user asks for anything else, run setup first.

## 1. Find streams (optional)

`"$PY" find_streams.py [--query "GTA 6 stream"] [--when today|week] [--max 8]`

Lists the most viewed GTA 6 streams with their length. Pick the top 2 or 3 unless the user names streamers. Long VODs (2h+) from big streamers are best. Streams that are live right now are skipped by default; clip them once the VOD is up (on YouTube that's usually right after the stream ends).

## 2. Listen (one stream at a time)

`"$PY" analyze.py "<url>" [--top 25] [--model small]`

- Downloads only the audio (a few hundred MB, not the video).
- Measures loudness every second, pulls YouTube's most-replayed graph, and on YouTube VODs of live streams reads the chat replay to measure chat speed and reactions ("LMAO", "CLIP IT", "???"). Twitch and Kick get loudness only; say so if asked.
- Turns that into one hype curve, takes the top 25 spikes, and transcribes a window around each one (about 2 minutes on long streams, 1 minute on videos under 30 minutes) with Whisper on the user's computer.
- Writes `WORK/streams/<id>/for_claude.md` (what you read), `candidates.json`, `hype.png` (show it, it's a good screen share) and `meta.json`.

Speed: `--model base` is about 2x faster than `small` with slightly rougher transcripts. `--full` transcribes the entire stream (slow, but useful when a stream is quiet and talky, like a podcast). You can run analyze on several streams one after another in the background.

## 3. Pick (this is your job, be harsh)

Read every `for_claude.md` for this batch, then `WORK/preferences.md` (the user's own rules, which override the defaults below when they conflict).

For each candidate, decide KEEP or CUT. **A clip is KEEP only if all three are yes:**
1. **Would a stranger stop scrolling in 2 seconds?** The first line or the first visible beat has to be the reaction, the shock, the joke. Not the setup.
2. **Does it make sense with zero context?** No "wait, what happened earlier", no inside jokes, no references to a chat message we can't see.
3. **Does it pay off inside the clip?** It ends on the punchline, the reveal or the reaction, never halfway through a thought.

Also cut: anything that opens with filler ("uh, so yeah", "okay so"), long silent stretches, the streamer reading donations, sponsor reads, ads, music-only stretches (copyright claims), anything sexual, hateful or targeting a real person, and anything that only works as audio-off gameplay with no reaction. Never pick the same moment twice. Big laughter or screaming with no speech can still be a KEEP if the hype score is high and the window around it explains itself.

Moment types to label: `first-reaction`, `freak-out`, `discovery`, `funny-fail`, `hot-take`, `skill-moment`, `rage`, `wholesome`, `glitch`.

Score every KEEP 1 to 10 for how hard it would stop a scroll. Keep only 7+. Aim for about 3 per stream, never pad with weak ones. If a stream has nothing good, say so; that's useful information, not a failure.

Set tight times: start 0.5 to 1 second before the first important word or reaction, end right after the payoff. Usually 15 to 45 seconds, never under 8 or over 90.

Write `WORK/picks.json` (overwrite it for each batch):

```json
{
  "picks": [
    {
      "source": "<stream id from meta.json>",
      "start": "01:23:41",
      "end": "01:24:09",
      "moment_type": "freak-out",
      "score": 9,
      "streamer": "Kai Cenat",
      "hook": "HE WAS NOT READY FOR THIS",
      "title": "Kai Cenat loses it at the GTA 6 police chase",
      "caption": "The second he saw the helicopter 💀 Credit: Kai Cenat (link in comments)",
      "hashtags": ["#gta6", "#kaicenat", "#gaming", "#shorts"],
      "why": "Screams in the first second, makes sense alone, ends on the crash"
    }
  ]
}
```

Hook rules: 3 to 7 words, ALL CAPS, the way a person would say it ("HE WAS NOT READY FOR THIS"), never a description ("STREAMER REACTS TO CHASE"), no fake claims about what's in the clip. Titles under 60 characters and lead with the person and the moment. Captions are one honest line plus a credit to the streamer. 3 to 5 hashtags. Write the hook and caption in the same language the streamer speaks (the burned-in captions are in that language too), unless the user asks for another one.

Before writing the file, show the user a short table (time, streamer, type, score, hook, why) and the moments you cut with a one-line reason each. Then continue unless they want changes.

## 4. Cut

1. `"$PY" cut.py download` downloads only the minutes each pick needs (plus 1.5 seconds on each side), saves three frames per clip in `<run>/frames/` (`<key>_a.jpg` near the start, `_b` in the middle, `_c` near the end), and prints the run folder.
2. **Look at all three frames of every clip** (open them with your Read tool). Streams often switch layouts (a full-screen camera, a BRB screen, a menu), so check the face cam is in the same place in all three. If the layout changes inside the clip, open `<key>_sheet.jpg` (one frame every 2 seconds, left to right, top to bottom, starting at the clip's start time) to see exactly when it switches, then move the pick's start or end so the whole clip uses one layout and run `download` again for that pick. Only use `facecam: null` when the whole clip is a full-screen camera or gameplay with no face cam. Then fill in `<run>/layout.json` for each key:
   - `"facecam": [x, y, w, h]` as fractions of the image (0 to 1) around the streamer's face cam box, tight to the box edges, or `null` if there's no face cam (full-screen camera or gameplay only).
   - `"focus_x"`: where the action is horizontally in the gameplay (0 left, 0.5 center, 1 right). For a full-screen camera with no gameplay, set it to the person's horizontal center and keep `facecam` null.
   Example: a face cam in the bottom-right corner of a 1920x1080 frame at pixels (1450, 700) to (1900, 1060) is `[0.755, 0.648, 0.234, 0.333]`.
3. `"$PY" cut.py render --run "<run folder>"` builds every clip: face cam on top (40%), gameplay underneath, the hook in a yellow box for the first 3 seconds, word-by-word captions from a fresh Whisper pass on the clip itself, audio normalized to Shorts loudness, and saves to `<run>/clips/`. Then it checks each clip for length, a black face cam area, black gameplay and missing captions.
4. If a check fails, or the user wants a change, fix `layout.json` or `picks.json` (times, hook) and re-render just that clip: `"$PY" cut.py render --run "<run>" --only 03`. For new times, edit the pick and run `download` again on a picks file with just that pick.
5. Look at a frame from the start and the middle of each finished clip yourself (`~/.gta6-clipper/bin/ffmpeg -ss 2 -i clip.mp4 -frames:v 1 check.jpg`, then again at the midpoint) before you say it's done. If the face is cut off, the crop is wrong or the captions read wrong, fix it and re-render.

## 5. Post

`"$PY" gallery.py --run "<run folder>"` opens one page with every clip (best first), its title, caption and hashtags, copy buttons and a link to the exact second in the source stream.

Tell the user, every time, in one or two lines:
- Watch each clip before posting and cut anything that starts slow.
- Add something of their own (their hook, a reaction, a take). Channels of raw reposted clips get turned down for monetization; "the clips are the reach, you are the channel".
- Credit the streamer, follow the clipping campaign's rules, and don't post the same clip twice on one account.

There is no auto-upload in this skill. Posting stays with the user so nothing goes out unreviewed.

## 6. Look at what's working (weekly)

`"$PY" learn.py --channel https://www.youtube.com/@<their handle>`

Reads the public views on their Shorts tab, matches each Short to the clips in `WORK/log.csv` by title, and reports average views by moment type and by streamer, plus the top 5 and bottom 5. It only matches Shorts whose title still contains the clip's title or hook, so tell users to keep that.

Then update `WORK/preferences.md` with 2 to 5 concrete rules from the data ("freak-outs do 2.1x my average, prefer them", "Kai clips beat xQc clips 3 to 1", "hooks that name the streamer beat hooks that don't"), and show the user what you changed. Section 3 reads this file every time, so the picks get better each week. Don't invent patterns from fewer than 10 matched clips; say there isn't enough data yet.

## Troubleshooting

- **"This stream is still live"**: analyze.py stops on live streams and on YouTube recordings that are still processing. Tell the user to come back once the stream has ended and the recording is up, or pick a different stream.
- **"Sign in to confirm you're not a bot" or 403 from YouTube:** set the browser to borrow cookies from (`export GTA6_COOKIES_BROWSER=chrome`, or safari/firefox) and run again. Also run setup again to update yt-dlp, which fixes most YouTube breakages.
- **No chat speed:** only YouTube VODs of live streams have chat replay. Loudness and most-replayed still work.
- **Most-replayed missing:** new or low-view videos don't have the graph yet. Loudness carries it.
- **A clip has no captions:** there was no clear speech (a pure scream). That's fine; the hook still shows.
- **Captions look wrong:** captions already use the `small` Whisper model. If a line is still wrong (loud music, people talking over each other), re-render that clip with `--only <key> --model medium` (slower, downloads once), or trim the clip around it.
- **Very slow transcribing:** use `--model base` or `--top 15`.
- Everything is in `WORK`. A stream's audio can be deleted after its clips are made.

## What not to do

- Never clip or post anything the user hasn't seen; never claim a clip is good without looking at it.
- Never pick from a stream the user doesn't have the right to clip if they tell you a campaign's rules forbid it.
- Never make up numbers about how a clip will perform.
