/* global Tone */
const TOTAL_SECONDS = 240; // compress the full time range into ~4 minutes
const SCALE = [36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82]; // C minor pentatonic, 4 octaves

const statusEl = document.getElementById("status");
const nowEl = document.getElementById("now");
const playBtn = document.getElementById("play");
const stopBtn = document.getElementById("stop");

let quakes = [];

fetch("/quakes.json")
  .then((r) => r.json())
  .then((data) => {
    quakes = data;
    statusEl.textContent = `${quakes.length.toLocaleString()} earthquakes loaded. Press Play.`;
    playBtn.disabled = false;
  })
  .catch(() => (statusEl.textContent = "Failed to load quakes.json — run the data prep script."));

function midiToNote(midi) {
  return Tone.Frequency(midi, "midi").toNote();
}

async function play() {
  await Tone.start();
  Tone.getTransport().cancel();

  const synth = new Tone.PolySynth(Tone.Synth, {
    envelope: { attack: 0.01, decay: 0.3, sustain: 0.2, release: 1.5 },
  });
  const panner = new Tone.Panner(0).toDestination();
  synth.connect(panner);
  synth.maxPolyphony = 64;

  const t0 = quakes[0].t;
  const t1 = quakes[quakes.length - 1].t;

  for (const q of quakes) {
    const when = ((q.t - t0) / (t1 - t0)) * TOTAL_SECONDS;
    const depthNorm = Math.min(q.depth, 700) / 700;
    const midi = SCALE[Math.round((1 - depthNorm) * (SCALE.length - 1))];
    const velocity = Math.min(1, 0.2 + ((q.mag - 5) / 4) * 0.8);
    const duration = 0.3 + (q.mag - 5) * 0.8;

    Tone.getTransport().schedule((time) => {
      panner.pan.setValueAtTime(Math.max(-1, Math.min(1, q.lon / 180)), time);
      synth.triggerAttackRelease(midiToNote(midi), duration, time, velocity);
      Tone.getDraw().schedule(() => {
        nowEl.innerHTML = `<span class="mag">M${q.mag.toFixed(1)}</span> &mdash; ${q.place} (${new Date(q.t).toISOString().slice(0, 10)})`;
      }, time);
    }, when);
  }

  Tone.getTransport().schedule(() => stop(), TOTAL_SECONDS + 2);
  Tone.getTransport().start();
  playBtn.disabled = true;
  stopBtn.disabled = false;
  statusEl.textContent = "Playing…";
}

function stop() {
  Tone.getTransport().stop();
  Tone.getTransport().cancel();
  playBtn.disabled = false;
  stopBtn.disabled = true;
  statusEl.textContent = "Stopped.";
}

playBtn.addEventListener("click", play);
stopBtn.addEventListener("click", stop);
playBtn.disabled = true;
