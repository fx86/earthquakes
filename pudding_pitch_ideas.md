# Pitch Ideas for The Pudding — Earthquake Data

Based on `earthquakes.data/all_earthquakes.csv` (1.24M events, 1900–2018, global, USGS-sourced) and `seismic_networks.csv` (1,625 monitoring networks with start/end years).

## What The Pudding is actually looking for

From [pudding.cool/pitch](https://pudding.cool/pitch/) and a contributor's [behind-the-scenes account](https://pudding.cool/process/pitching-gendered-descriptions/):

- **Worthy of public discourse** — would people debate the premise for 20 minutes? What assumption does it challenge?
- **A deeper truth** — does the reader leave feeling differently, even if the insight is buried in the piece?
- **Show, not tell** — the visual does the arguing, not the prose.
- They reject good *hooks* with weak *data* (see the Trader Joe's parking lot pitch that got turned down for not having a real finding). Have the finding nailed down before pitching, not just an interesting dataset.
- Pitch via [this form](https://forms.gle/mKU3DSqtdVmeN8Lb7), reviewed monthly (first week of the month). Compensation is $7,200 for end-to-end work, less if Pudding handles design/code.
- No existing Pudding piece on earthquake/seismic data turned up in search — this lane looks open.

## Ranked ideas

### 1. "We can hear North Korea's nuclear tests" — strongest pitch
Every DPRK nuclear test (2006, 2009, 2013, Jan 2016, Sep 2016, 2017) shows up in the dataset as a discrete seismic event, with magnitude climbing each time: 4.3 → 4.7 → 5.1 → 5.1 → 5.3 → 6.3 (the last being the H-bomb test). A scrollytelling piece walking through each test as a magnitude spike, translating that into bomb yield, ending on the 2017 test dwarfing the rest. Concrete, finishable, geopolitically resonant, and the data already supports the full narrative — exactly the kind of pitch that survived the "is there really a story here" gut check.

### 2. "Earthquakes aren't increasing. Our ears are." — flagship, most "Pudding voice"
Yearly event counts jump from ~20–30k/year (2004–2012) to 94k in 2013 and 120–130k/year after — but `seismic_networks.csv` shows new networks coming online at ~70–100/year in that same window. This is a myth-bust: the chart that looks like "the world is shaking more" actually shows "we built more sensors." Challenges a real public assumption (often repeated after big quakes), has a clean reveal, and visualizes well as a synced network-growth map + quake-count chart ticking forward together.

### 3. "The shape of risk" — depth × magnitude by region
Subduction-zone countries (Japan, Chile, Indonesia — all in the top of the dataset) produce shallow, large quakes; other regions cluster differently. A scrollable map/strip comparing depth profiles by country, answering "why does it shake the way it does, here."

### 4. "What's under your house" — personalized interactive
User drops a pin or types a location; see every recorded quake nearby, the biggest one, how often. Personalization + a real "oh" moment is a recurring Pudding format (e.g. their Spotify and parking-lot pieces).

### 5. Man-made shaking
`type` field separates natural earthquakes from quarry blasts, mining/nuclear explosions. Mapping non-natural seismic events against natural ones, by industry and region — "the ground noise we cause ourselves."

## Strengthening the data before pitching

For idea #2 specifically, the network-level `Start Year` in `seismic_networks.csv` is a blunt proxy — one "network" can be 1 station or 4,000. A sharper version: pull per-station deployment history from the **IRIS/EarthScope FDSNWS-Station service** (`level=station`, free, text or XML), which gives every individual global seismic station with exact start/end dates. Plotting *actual station count per year* against *quake count per year* would make the "detection, not increase" case far more rigorous — this is the kind of "show, not tell" evidence that turns a hunch into a pitch The Pudding can say yes to.

`http://service.iris.edu/fdsnws/station/1/query?level=station&format=text&starttime=1900-01-01&endtime=2026-01-01`

## Suggested next step

Pick one idea, nail the underlying finding with real numbers/chart (not just a hook), then submit via the [pitch form](https://forms.gle/mKU3DSqtdVmeN8Lb7).
