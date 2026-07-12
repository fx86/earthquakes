/* global Tone */
const TOTAL_SECONDS = 240; // compress the full time range into ~4 minutes
const SCALE = [36, 38, 41, 43, 46, 48, 50, 53, 55, 58, 60, 62, 65, 67, 70, 72, 74, 77, 79, 82]; // C minor pentatonic, 4 octaves

// Real CC0 drum recordings (VCSL) graded small -> huge, one per key.
// Triggering the exact key plays the recording unpitched.
function makeTaiko() {
  return new Tone.Sampler({
    urls: {
      C5: "drum1.wav", // high tom, stick — shime-daiko
      C4: "drum2.wav", // high tom, mallet
      C3: "drum3.wav", // low tom, mallet — chu-daiko
      C2: "drum4.wav", // concert bass drum
      C1: "drum5.wav", // concert bass drum, hardest hit — o-daiko
    },
    baseUrl: "/samples/taiko/",
  });
}

// Synthesized instrument presets (offline — no sample downloads)
const INSTRUMENTS = {
  "Taiko drums": makeTaiko,
  Cello: () =>
    new Tone.PolySynth(Tone.AMSynth, {
      harmonicity: 3.01,
      oscillator: { type: "sawtooth" },
      envelope: { attack: 0.18, decay: 0.3, sustain: 0.8, release: 1.4 },
      modulation: { type: "square" },
      modulationEnvelope: { attack: 0.3, decay: 0.5, sustain: 0.4, release: 1.2 },
    }),
  "Acoustic guitar": () =>
    new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "fmtriangle", harmonicity: 2, modulationIndex: 3 },
      envelope: { attack: 0.002, decay: 0.5, sustain: 0.05, release: 0.4 },
    }),
  Piano: () =>
    new Tone.PolySynth(Tone.Synth, {
      oscillator: { type: "triangle" },
      envelope: { attack: 0.005, decay: 1.2, sustain: 0.15, release: 1.6 },
    }),
};

// Isle of Dogs-style graded taiko ensemble: bigger quakes strike bigger drums.
// Values are the sampler keys above, small drum -> big drum.
const TAIKO_DRUMS = [72, 60, 48, 36, 24]; // C5, C4, C3, C2, C1
const MAG_MIN = 6.5;
const MAG_MAX = 9.2;

function taikoPitch(mag) {
  // Drum changes align with the Richter buckets; M8.6+ gets the deepest o-daiko
  const thresholds = [7, 7.5, 8, 8.6];
  let i = 0;
  while (i < thresholds.length && mag >= thresholds[i]) i++;
  return TAIKO_DRUMS[i];
}

// Shared mapping: quake features -> note parameters
function noteFor(instrument, mag, depth) {
  const depthNorm = Math.min(depth, 700) / 700;
  const midi = instrument === "Taiko drums"
    ? taikoPitch(mag)
    : SCALE[Math.round((1 - depthNorm) * (SCALE.length - 1))];
  const velocity = Math.min(1, 0.2 + ((mag - 5) / 4) * 0.8);
  const duration = 0.3 + (mag - 5) * 0.8;
  return { midi, velocity, duration };
}

// Richter buckets, lightest -> heaviest, with default instruments
const BUCKETS = [
  { label: "6.5–7", max: 7, instrument: "Taiko drums" },
  { label: "7–7.5", max: 7.5, instrument: "Taiko drums" },
  { label: "7.5–8", max: 8, instrument: "Taiko drums" },
  { label: "8+", max: Infinity, instrument: "Taiko drums" },
];

const statusEl = document.getElementById("status");
const nowEl = document.getElementById("now");
const playBtn = document.getElementById("play");
const stopBtn = document.getElementById("stop");

// Preview sliders
const prevMag = document.getElementById("prevMag");
const prevDepth = document.getElementById("prevDepth");
prevMag.addEventListener("input", () => (document.getElementById("prevMagVal").textContent = prevMag.value));
prevDepth.addEventListener("input", () => (document.getElementById("prevDepthVal").textContent = prevDepth.value));

const previewSynths = {};
async function preview(instrument, mag) {
  await Tone.start();
  if (!previewSynths[instrument]) {
    previewSynths[instrument] = INSTRUMENTS[instrument]().connect(Tone.getDestination());
  }
  await Tone.loaded();
  const depth = parseFloat(prevDepth.value);
  const { midi, velocity, duration } = noteFor(instrument, mag, depth);
  previewSynths[instrument].triggerAttackRelease(midiToNote(midi), duration, Tone.now(), velocity);
  if (instrument === "Taiko drums") {
    const drumIdx = TAIKO_DRUMS.indexOf(midi) + 1;
    statusEl.textContent = `Preview: M${mag.toFixed(1)} → drum ${drumIdx}/${TAIKO_DRUMS.length} (deeper = bigger)`;
  } else {
    statusEl.textContent = `Preview: ${instrument} @ M${mag.toFixed(1)}, ${depth} km deep`;
  }
}

// Build one dropdown per Richter bucket
const instrumentsEl = document.getElementById("instruments");
let bucketMin = MAG_MIN;
for (const bucket of BUCKETS) {
  const lo = bucketMin;
  const hi = Math.min(bucket.max - 0.01, MAG_MAX); // keep the clamp inside the bucket
  bucketMin = bucket.max;
  const row = document.createElement("div");
  row.className = "bucket-row";
  const label = document.createElement("label");
  label.textContent = `M ${bucket.label}`;
  const select = document.createElement("select");
  for (const name of Object.keys(INSTRUMENTS)) {
    const opt = document.createElement("option");
    opt.value = name;
    opt.textContent = name;
    opt.selected = name === bucket.instrument;
    select.appendChild(opt);
  }
  select.addEventListener("change", () => (bucket.instrument = select.value));
  const test = document.createElement("button");
  test.className = "test";
  test.textContent = "\u266a Test";
  test.title = "Play this instrument at the preview magnitude (clamped to this Richter range) and depth";
  test.addEventListener("click", () => {
    // Clamp the global preview magnitude into this bucket's range so each row sounds like its own quakes
    const mag = Math.min(Math.max(parseFloat(prevMag.value), lo), hi);
    preview(select.value, mag);
  });
  row.append(label, select, test);
  instrumentsEl.appendChild(row);
}

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

let activeSynths = [];

function disposeSynths() {
  for (const s of activeSynths) s.dispose();
  activeSynths = [];
}

async function play() {
  await Tone.start();
  Tone.getTransport().cancel();
  disposeSynths();

  const panner = new Tone.Panner(0).toDestination();
  activeSynths.push(panner);

  // One synth per bucket, based on the current dropdown choices
  const bucketSynths = BUCKETS.map((bucket) => {
    const synth = INSTRUMENTS[bucket.instrument]();
    if (synth.maxPolyphony !== undefined) synth.maxPolyphony = 48;
    synth.connect(panner);
    activeSynths.push(synth);
    return synth;
  });

  const synthFor = (mag) => {
    const idx = BUCKETS.findIndex((b) => mag < b.max);
    return { synth: bucketSynths[idx], instrument: BUCKETS[idx].instrument };
  };

  statusEl.textContent = "Loading samples…";
  await Tone.loaded();

  const t0 = quakes[0].t;
  const t1 = quakes[quakes.length - 1].t;

  for (const q of quakes) {
    const when = ((q.t - t0) / (t1 - t0)) * TOTAL_SECONDS;
    const { synth, instrument } = synthFor(q.mag);
    const { midi, velocity, duration } = noteFor(instrument, q.mag, q.depth);

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
  disposeSynths();
  playBtn.disabled = false;
  stopBtn.disabled = true;
  statusEl.textContent = "Stopped.";
}

playBtn.addEventListener("click", play);
stopBtn.addEventListener("click", stop);
playBtn.disabled = true;
