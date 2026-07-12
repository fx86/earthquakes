import pandas as pd
from midiutil import MIDIFile

df = pd.read_csv("all_earthquakes.csv", low_memory=False).head(2000)
df["time"] = pd.to_datetime(df["time"], errors="coerce", utc=True)
df = df.dropna(subset=["time", "mag", "depth"])
df = df[df.mag >= 5].sort_values("time")  # keep it listenable

t0, t1 = df.time.min(), df.time.max()
total_beats = 480  # ~4 min at 120 bpm

midi = MIDIFile(1)
midi.addTempo(0, 0, 120)

seen = set()  # midiutil crashes on same-pitch notes starting at the same beat
for _, q in df.iterrows():
    beat = (q.time - t0) / (t1 - t0) * total_beats
    pitch = int(96 - (min(q.depth, 700) / 700) * 48)      # deep = low
    velocity = int(min(127, 40 + (q.mag - 5) / 4 * 87))   # mag 5→40, 9→127
    duration = 0.5 + (q.mag - 5)                          # big quakes ring out
    key = (pitch, round(beat, 3))
    if key in seen:
        continue
    seen.add(key)
    midi.addNote(0, 0, pitch, beat, duration, velocity)

with open("earthquakes.mid", "wb") as f:
    midi.writeFile(f)