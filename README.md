# rocky-peon-ping

A [peon-ping](https://openpeon.com) voice pack featuring **Rocky**, the Eridian engineer from Andy Weir's *Project Hail Mary*.

Rocky-speak hallmarks: dropped articles, triple-word emphasis (`good good good`), `question?` suffix on interrogatives, and two bonus conventions from this pack:

- `"fist bump"` — Rocky's thumbs up
- `"brave brave"` — Rocky's way of calling you dumb (affectionate)

All 50 clips were produced with YourTTS zero-shot voice cloning from a scrubbed reference of Rocky's film dialogue, then speed-adjusted to **1.3x** for a punchier peon-ping feel.

Built on top of [Pedram Amini's rocky_say gist](https://gist.github.com/pedramamini/fa5f6ef99dae79add220188419230642).

## Contents

```
.
├── rocky_pack/                   # the finished voice pack (ready to install)
│   ├── openpeon.json             # manifest: 50 clips across 6 categories
│   └── sounds/                   # 50 × WAV, mono 16 kHz, 1.3x speed
├── rocky_say                     # Rocky TTS CLI (local-folder variant)
├── generate_pack.py              # regenerate the whole pack in one pass
├── .gitignore
└── README.md
```

The voice reference `rocky_training_audio_scrubbed.wav` and downloaded TTS model weights (~2 GB) are **not** committed — you download them during setup.

---

## Quick start — just install the pack

If you already have [peon-ping](https://openpeon.com) set up and only want to use the clips:

```bash
# 1. Clone and install
git clone https://github.com/Akshat1903/rocky-peon-ping.git
cd rocky-peon-ping
cp -r rocky_pack ~/.openpeon/packs/rocky

# 2. Verify it's recognized
bash ~/.claude/hooks/peon-ping/peon.sh packs list | grep rocky

# 3. Try a preview (plays all clips in a category)
# Note: peon-ping's `preview` reads default_pack. Easiest way to test:
#   (a) set rocky as default, then preview, then revert
bash ~/.claude/hooks/peon-ping/peon.sh preview task.complete   # if rocky is default
```

### Using it only in one Claude Code session

Inside a Claude Code chat:

```
/peon-ping-use rocky
```

This flips peon-ping into `session_override` mode and maps the current session to the rocky pack. All future events (task complete, errors, etc.) during that chat will play Rocky clips.

### Using it as your default pack everywhere

Edit `~/.claude/hooks/peon-ping/config.json` and set:

```json
"default_pack": "rocky"
```

---

## Category coverage

| Category | Clips | Example |
|---|---|---|
| `session.start` | 8 | *"Rocky here. Ready work, question?"* |
| `task.acknowledge` | 8 | *"Rocky got it. Fist bump!"* |
| `task.complete` | 9 | *"Done done done! Fist bump!"* |
| `task.error` | 8 | *"Bad bad bad. Rocky sorry."* |
| `input.required` | 8 | *"Friend, question? Rocky need you."* |
| `user.spam` | 9 | *"Human brave brave. Patience, question?"* |

**Total:** 50 clips, ~4.5 MB.

---

## Rebuild or extend the pack

Want to add your own Rocky lines (or swap out mine)? Here's the full local-dev path.

### 1. System dependencies (macOS)

```bash
brew install ffmpeg python@3.11
```

On Debian/Ubuntu:

```bash
sudo apt install ffmpeg python3.11 python3.11-venv
```

Python **3.11** is important — `coqui-tts` doesn't support 3.13+ yet.

### 2. Clone and create the venv

```bash
git clone https://github.com/Akshat1903/rocky-peon-ping.git
cd rocky-peon-ping
python3.11 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install coqui-tts 'transformers==4.44.0' 'torch==2.5.1' 'torchaudio==2.5.1'
```

This pulls ~2 GB of PyTorch wheels. Grab a coffee.

### 3. Download Rocky's voice reference (22 MB)

The reference audio is hosted by Pedram (original author of the gist this pack builds on):

```bash
curl -L -o rocky_training_audio_scrubbed.wav \
  https://pedramamini.com/dropbox/rocky_training_audio_scrubbed.wav
```

It must live in the repo root next to `rocky_say` — `generate_pack.py` expects it there.

### 4. Make rocky_say executable

```bash
chmod +x rocky_say
```

### 5. Test a one-off line

```bash
./rocky_say "Hello, how are you doing today?"
```

First run downloads the YourTTS model weights (~400 MB, cached in `./tts_cache/`). Subsequent runs are ~2 seconds.

Useful flags:

```bash
./rocky_say --transform-only "What do you mean?"     # just see the Rocky-speak text
./rocky_say --raw "Speak exactly this"               # skip the auto-transform
./rocky_say -o out.wav "Save to file"
./rocky_say -s 1.3 "Adjust speed"
```

The transform engine is rule-based — it drops articles, triples emphasis words, and adds the `, question?` suffix. See the `EMPHASIS_MAP` and `PHRASE_MAP` tables inside `rocky_say` to tweak the dictionary.

---

## Add new clips to the pack

All pack content lives in one list inside `generate_pack.py`. Each entry is:

```python
# (filename,              category,            text,                                    label)
("MyNewClip.wav",         "task.complete",     "Rocky finish task! Fist bump friend.",  "Rocky finish, fist bump"),
```

### Step-by-step

1. **Pick a category.** Must match one of `openpeon.json`'s keys:
   `session.start`, `task.acknowledge`, `task.complete`, `task.error`, `input.required`, `user.spam`.

2. **Draft the line** in Rocky-speak (or let the transform engine do it by running `./rocky_say --transform-only "your english line"` first).

3. **Pick a short, unique filename** (letters, numbers, dots, hyphens, underscores only — spec requirement).

4. **Add the tuple** to the `CLIPS` list in `generate_pack.py`. Keep entries grouped by category; order inside a category is preserved in the manifest.

5. **Regenerate:**

   ```bash
   ./venv/bin/python3 generate_pack.py
   ```

   Takes ~30 seconds total for all 50+ clips. The script:
   - loads YourTTS once (reuses the cached model)
   - renders every line in `CLIPS` to `rocky_pack/sounds/*.wav`
   - applies 1.3x ffmpeg atempo to each
   - rewrites `rocky_pack/openpeon.json` with fresh sha256 hashes

6. **Reinstall the pack** into peon-ping:

   ```bash
   rsync -a --delete rocky_pack/ ~/.openpeon/packs/rocky/
   ```

   The `--delete` flag removes any orphaned files in the installed pack if you deleted clips.

7. **Listen:**

   ```bash
   afplay rocky_pack/sounds/MyNewClip.wav
   ```

### Tuning tips

- **"Rocky" sounds stretched.** YourTTS lingers on isolated proper nouns. Either bump `SPEED` in `generate_pack.py` higher (1.35 is noticeable), or rephrase to put "Rocky" mid-sentence: `"Hello friend! Rocky arrive."` sounds better than `"Rocky arrive! Hello friend!"`.
- **Triple-word emphasis lands flat.** Vary it: `"happy happy happy"` works, but `"good, good good"` (with a comma) gives YourTTS more prosody room.
- **Clip feels too short.** Short utterances (1-3 words) sometimes trip the model. Pad with filler: `"Yes yes yes. Rocky do."` reads better than `"Yes!"`.
- **Clip feels too long.** openpeon.com caps individual clips at 1 MB and recommends 1–5 seconds. At 1.3x speed with 16 kHz mono, you can fit ~20 seconds in a megabyte — length mostly matters for UX.

### Bulk-changing speed across the whole pack

Edit `SPEED = 1.3` at the top of `generate_pack.py` and re-run. Every clip regenerates from raw YourTTS output at the new speed — no stacking ffmpeg filters.

---

## Advanced: XTTS v2 instead of YourTTS

`rocky_say` also supports XTTS v2 via a persistent local server. It's slower and, in this pack's experience, worse on short proper nouns — but it can sound better on longer narrative lines. If you want to experiment:

```bash
./rocky_say --server start          # ~17s cold start, loads XTTS v2
./rocky_say -m xtts "Hello friend"  # ~3s per call after
./rocky_say --server stop
```

XTTS v2 requires a one-time license acceptance (non-commercial CPML). The repo's `rocky_say` sets `COQUI_TOS_AGREED=1` automatically — use at your own discretion and only for non-commercial projects.

---

## Credits

- **[Pedram Amini](https://pedramamini.com/)** — original [`rocky_say` gist](https://gist.github.com/pedramamini/fa5f6ef99dae79add220188419230642), reference audio scrubbing, Rocky-speak transform engine.
- **Andy Weir** — *Project Hail Mary* and Rocky himself.
- **[Coqui TTS](https://github.com/idiap/coqui-ai-TTS)** — YourTTS / XTTS v2 voice cloning.
- **[openpeon](https://openpeon.com)** — the pack spec and runtime.

## License

Pack assets: **CC-BY-NC-4.0** — personal, non-commercial use only.

The source voice and character design are the IP of *Project Hail Mary*'s production company. YourTTS and XTTS v2 ship under Coqui's non-commercial terms. Don't ship this in anything you're selling.
