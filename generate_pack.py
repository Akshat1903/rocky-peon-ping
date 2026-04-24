#!/usr/bin/env python3
"""One-shot generator for the Rocky peon-ping pack.

Loads YourTTS once, synthesizes all clips, applies 1.1x speed via ffmpeg.
Output: rocky_pack/sounds/*.wav
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ["TTS_HOME"] = os.path.join(ROOT, "tts_cache")
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["COQUI_TOS_AGREED"] = "1"

MODEL = "tts_models/multilingual/multi-dataset/your_tts"

REFERENCE = os.path.join(ROOT, "rocky_training_audio_scrubbed.wav")
PACK_DIR = os.path.join(ROOT, "rocky_pack")
SOUNDS_DIR = os.path.join(PACK_DIR, "sounds")
SPEED = 1.1

# (filename, category, text, label)
CLIPS = [
    # session.start
    ("ReadyWork.wav", "session.start", "Rocky here. Ready work, question?", "Rocky here, ready work"),
    ("HelloFriend.wav", "session.start", "Hello friend! Rocky ready. Fist bump!", "Hello friend, fist bump"),
    ("GoodMorning.wav", "session.start", "Good morning, question? Rocky say good good good.", "Good morning"),
    ("AwakeAwake.wav", "session.start", "Rocky awake awake awake. What we build, question?", "Rocky awake, what we build"),
    ("NewDay.wav", "session.start", "Amaze amaze amaze! New day, new code.", "New day, new code"),
    ("RockyArrive.wav", "session.start", "Rocky arrive! You friend, question?", "Rocky arrive"),
    ("BrainHere.wav", "session.start", "Hello human! Rocky bring brain.", "Rocky bring brain"),
    ("ScienceTime.wav", "session.start", "Science time! Rocky excite excite excite.", "Science time"),

    # task.acknowledge
    ("Understand.wav", "task.acknowledge", "Understand understand understand.", "Understand"),
    ("GotItFistBump.wav", "task.acknowledge", "Rocky got it. Fist bump!", "Rocky got it, fist bump"),
    ("YesYesYes.wav", "task.acknowledge", "Yes yes yes. Rocky do.", "Yes yes yes, Rocky do"),
    ("GoodIdea.wav", "task.acknowledge", "Good idea! Rocky try.", "Good idea"),
    ("RockyListen.wav", "task.acknowledge", "Rocky listen. Work now.", "Rocky listen, work now"),
    ("OkayOnIt.wav", "task.acknowledge", "Okay okay okay. On it.", "Okay, on it"),
    ("KnowWhatDo.wav", "task.acknowledge", "Rocky know what do. Work work work.", "Rocky know what to do"),
    ("FistBumpUnderstand.wav", "task.acknowledge", "Fist bump! Rocky understand.", "Fist bump, Rocky understand"),

    # task.complete
    ("DoneFistBump.wav", "task.complete", "Done done done! Fist bump!", "Done, fist bump"),
    ("HappyFinish.wav", "task.complete", "Finish! Rocky happy happy happy.", "Finish, Rocky happy"),
    ("GoodEngineer.wav", "task.complete", "Rocky good engineer, question? Work complete.", "Rocky good engineer"),
    ("TaskDone.wav", "task.complete", "Task done. Good good good.", "Task done, good"),
    ("FistBumpFriend.wav", "task.complete", "Fist bump, friend! Rocky finish.", "Fist bump friend"),
    ("RockyProud.wav", "task.complete", "Work done. Rocky proud proud proud.", "Rocky proud"),
    ("AmazeWork.wav", "task.complete", "Amaze amaze amaze! Rocky make it work.", "Amaze, Rocky make it work"),
    ("CodeGood.wav", "task.complete", "Code good. Rocky solve.", "Code good, Rocky solve"),
    ("EasyEasy.wav", "task.complete", "Ha! Easy easy easy. Fist bump!", "Easy easy, fist bump"),

    # task.error
    ("BadBadBad.wav", "task.error", "Bad bad bad. Rocky sorry.", "Bad, Rocky sorry"),
    ("NoWork.wav", "task.error", "No work. Something break break break.", "Something break"),
    ("Confuse.wav", "task.error", "Ohhh. Rocky confuse confuse confuse.", "Rocky confuse"),
    ("ProblemNoUnderstand.wav", "task.error", "Problem. Rocky no understand.", "Rocky no understand"),
    ("SadSadSad.wav", "task.error", "Sad sad sad. Rocky try again, question?", "Sad, Rocky try again"),
    ("RockyFail.wav", "task.error", "Rocky fail. You help, question?", "Rocky fail, you help"),
    ("ErrorNoLike.wav", "task.error", "Error error error. Rocky no like.", "Error, Rocky no like"),
    ("TaskHard.wav", "task.error", "This task hard hard hard. Rocky stuck.", "Task hard, Rocky stuck"),

    # input.required
    ("NeedYou.wav", "input.required", "Friend, question? Rocky need you.", "Rocky need you"),
    ("WhatDo.wav", "input.required", "What do, question? Rocky wait wait wait.", "What do, Rocky wait"),
    ("YouThere.wav", "input.required", "Hello, question? You there, question?", "You there"),
    ("RockyStuck.wav", "input.required", "Rocky stuck. Need human, question?", "Rocky stuck, need human"),
    ("HelpWait.wav", "input.required", "Help help help. Rocky wait.", "Help, Rocky wait"),
    ("QuestionForFriend.wav", "input.required", "Question for friend, question?", "Question for friend"),
    ("NeedAnswer.wav", "input.required", "Rocky need answer. You tell, question?", "Rocky need answer"),
    ("ComeBack.wav", "input.required", "Friend! Come back. Rocky bored.", "Come back, Rocky bored"),

    # user.spam
    ("TooManyClick.wav", "user.spam", "Friend brave brave. Too many click.", "Too many click"),
    ("RockyBusy.wav", "user.spam", "Rocky busy! You brave brave.", "Rocky busy, you brave brave"),
    ("StopStopStop.wav", "user.spam", "Stop stop stop. Rocky working working working.", "Stop, Rocky working"),
    ("HumanBrave.wav", "user.spam", "Human brave brave. Patience, question?", "Human brave brave, patience"),
    ("WhyYouDoThis.wav", "user.spam", "Why you do this, question? Rocky sad.", "Why you do this, Rocky sad"),
    ("VeryBrave.wav", "user.spam", "You brave brave brave. Very brave.", "You brave brave"),
    ("NotFastButton.wav", "user.spam", "Rocky not fast button. You brave brave.", "Rocky not fast button"),
    ("HaImpatient.wav", "user.spam", "Ha! Human impatient. Brave brave.", "Human impatient, brave brave"),
    ("CountClick.wav", "user.spam", "Rocky count click. You very brave brave.", "Rocky count click"),

    # resource.limit
    ("BrainFull.wav", "resource.limit", "Ohh. Rocky brain full full full.", "Rocky brain full"),
    ("TooMuchWork.wav", "resource.limit", "Too much work. Rocky overload.", "Too much work, overload"),
    ("NeedRest.wav", "resource.limit", "Rocky need rest. Fuel low, question?", "Rocky need rest"),
    ("LimitReach.wav", "resource.limit", "Limit reach. Rocky stop.", "Limit reach, Rocky stop"),
    ("NoMoreFuel.wav", "resource.limit", "No more fuel. Rocky tired tired tired.", "No more fuel, Rocky tired"),
    ("TokenGone.wav", "resource.limit", "Token gone gone gone. Rocky wait.", "Token gone, Rocky wait"),
    ("BrainTired.wav", "resource.limit", "Brain tired. Too many think.", "Brain tired, too many think"),
    ("OverloadBreak.wav", "resource.limit", "Overload! Rocky need break, question?", "Overload, Rocky need break"),
]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def apply_speed(in_path, out_path, speed):
    subprocess.run(
        ["ffmpeg", "-y", "-i", in_path, "-filter:a", f"atempo={speed}", out_path],
        capture_output=True, check=True,
    )


def main():
    print(f"Loading {MODEL} (model cache: {os.environ['TTS_HOME']})...", flush=True)
    t0 = time.time()
    from TTS.api import TTS
    tts = TTS(MODEL)
    print(f"Model loaded in {time.time()-t0:.1f}s", flush=True)

    total = len(CLIPS)
    for i, (fname, category, text, label) in enumerate(CLIPS, 1):
        out = os.path.join(SOUNDS_DIR, fname)
        print(f"[{i}/{total}] {category:18s} {fname:28s} \"{text}\"", flush=True)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            raw = f.name
        try:
            tts.tts_to_file(text=text, speaker_wav=REFERENCE, language="en", file_path=raw)
            apply_speed(raw, out, SPEED)
        finally:
            if os.path.exists(raw):
                os.unlink(raw)

    print("\nBuilding openpeon.json manifest...", flush=True)
    categories = {}
    for fname, category, text, label in CLIPS:
        rel = f"sounds/{fname}"
        abs_path = os.path.join(SOUNDS_DIR, fname)
        entry = {
            "file": rel,
            "label": label,
            "sha256": sha256_file(abs_path),
        }
        categories.setdefault(category, {"sounds": []})["sounds"].append(entry)

    manifest = {
        "cesp_version": "1.0",
        "name": "rocky",
        "display_name": "Rocky (Project Hail Mary)",
        "version": "1.0.1",
        "description": "Rocky the Eridian from Project Hail Mary, synthesized via Chatterbox voice cloning. Dropped articles, triple-word emphasis, and the signature 'question?' suffix. Fist bump means thumbs up. Brave brave means dumb.",
        "author": {"name": "Akshat1903", "github": "Akshat1903"},
        "license": "CC-BY-NC-4.0",
        "language": "en",
        "categories": categories,
    }

    manifest_path = os.path.join(PACK_DIR, "openpeon.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Wrote {manifest_path}")
    print(f"\nTotal clips: {total}")
    print(f"Total time:  {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
